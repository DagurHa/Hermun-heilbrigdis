import numpy as np
import random
import time
import pandas as pd
import streamlit as st
import simpy as sp
import plotly.express as px
import plotly.graph_objects as go

TELJA = 0
TIMI = 0  #Byrjunartími hermunar (gæti verið useless)
#Hér eftir koma allar global breytur.
# Mismunandi stöður sjúklings. Bætum við og breytum þegar lengra er komið.
STATES = ["legudeild", "göngudeild", "dauði", "heim"]
AGE_GROUPS = ["Ungur","Miðaldra","Gamall"] # mismunandi aldurshópar sjúklings. Breytum/bætum við mögulega
# meðalfjöldi aldurshópa sem koma á spítala á dag, fáum rauntölur hér og getum síðan breytt
AGE_GROUP_AMOUNT = {
    AGE_GROUPS[0] : 10,
    AGE_GROUPS[1] : 15,
    AGE_GROUPS[2] : 30
}
# færslulíkur milli deilda, hér höfum við default færslulíkur sem verða vonandi byggðar á gögnum. 
# Síðan er líka hægt að breyta í streamlit.
PROB = {
    STATES[0] : [0.0, 0.3, 0.1, 0.6],
    STATES[1] : [0.0, 0.5, 0.0, 0.5],
    STATES[2] : [0.0, 0.0, 1.0, 0.0],
    STATES[3] : [0.0, 0.0, 0.0, 1.0]
}
INITIAL_PROB = [0.3, 0.7] # Upphafslíkur á að fara á legudeild og göngudeild (þessu mun verða breytt)
# meðalbiðtímar á göngu- og legudeild, þetta verður default biðin sem byggist nú á aldri og verður vonandi byggð á gögnum.
#Pæling að hafa dag-/göngudeild alltaf einn dag og einhverjar líkur á að göngu-/dagdeildarsjúklingar fari á legudeild
MEAN_WAIT_TIMES = {
    (AGE_GROUPS[0], STATES[0]) : 2.0, (AGE_GROUPS[0], STATES[1]) : 0.01,
    (AGE_GROUPS[1], STATES[0]) : 3.0, (AGE_GROUPS[1], STATES[1]) : 0.02,
    (AGE_GROUPS[2], STATES[0]) : 5.0, (AGE_GROUPS[2], STATES[1]) : 0.04
}
#Athuga gæti verið gott að setja default sim attributes lika
simAttributes = {
    "meðalfjöldi" : AGE_GROUP_AMOUNT,
    "Færslulíkur" : PROB,
    "Upphafslíkur" : INITIAL_PROB
}

deildaskipti = []

class Patient:
    def __init__(self,aldur,env,deild,numer):
        self.aldur = aldur
        self.env = env
        self.deild = deild
        self.timiSpitala = 0 # Þetta gæti verið gott í framtíð
        self.numer = numer # breyta fyrir aflúsun
    # Þegar sjúklingur er búinn á sinni deild finnum við hvert hann fer næst og sendum hann þangað
    def updatePatient(self,S):
        prev = self.deild
        #ATHUGA: einmitt núna er PROB global breyta sem ekki er hægt að breyta á streamlit
        new_deild = np.random.choice(STATES,p = PROB[prev])
        deildaskipti.append((prev,new_deild)) # listi heldur utan um hvert sjúklingur fer næst (eða verður kyrr)
        self.deild = new_deild
        if self.deild == STATES[2] or self.deild == STATES[3]:
            S.removeP(prev,self)
        else:
            S.fjoldi[prev] -= 1
            yield self.env.process(S.addP(self,True))


class Spitali:
    def __init__(self,fjoldi,env,simAttributes):
        self.const = simAttributes
        self.p_age = [(1.0/self.const["meðalbið"][age])/self.const["lambda"] for age in AGE_GROUPS]
        self.env = env
        self.cap = self.const["CAP"]
        self.fjoldi = fjoldi
        self.amount = sum(list(fjoldi.values()))
        self.action = env.process(self.patientGen(env))
    def patientGen(self,env):
        while True:
            try:
                wait = random.expovariate(self.const["lambda"])
                #print(f"Þurfum að bíða í {wait} langann tíma eftir næsta sjúkling, liðinn tími er {env.now}")
                yield env.timeout(wait)
                aldur = np.random.choice(AGE_GROUPS,p = self.p_age)
                deild = np.random.choice([STATES[0],STATES[1]],p = self.const["Upphafslíkur"])
                p = Patient(aldur,env,deild,TELJA)
                #print(f"Sjúklingur númer {p.numer} fer á {p.deild} og er {p.aldur}, liðinn tími er {env.now}")
                env.process(self.addP(p,False))
            except sp.Interrupt:
                pass
    # Bætum nýjum sjúklingi við á deildina sína og látum hann bíða þar
    def addP(self,p,innritaður):
        self.fjoldi[p.deild] += 1
        if not innritaður:
            global TELJA
            TELJA += 1
            self.amount += 1
            #print(f"fjöldi á spítala er núna {self.amount}, liðinn tími er {self.env.now}")
        wait = random.expovariate(1.0/MEAN_WAIT_TIMES[(p.aldur,p.deild)])
        #print(f"Sjúklingur númer {p.numer} á {p.deild} þarf að bíða þar í {wait}, liðinn tími er {self.env.now}")
        yield self.env.timeout(wait)
        yield self.env.process(p.updatePatient(self))
    # fjarlægjum sjúkling af deildinni prev
    def removeP(self,prev,p):
        #print(f"Sjúklingur númer {p.numer} fer af {prev} til {p.deild}, liðinn tími er {self.env.now}")
        self.amount -= 1
        self.fjoldi[prev] -= 1
        self.fjoldi[p.deild] += 1 # Ef sjúklingur er farinn af spítala er hann annað hvort dáinn eða farinn heim núna


def interrupter(env,S,STOP,data,showSim,chart):
    for i in range(STOP):
        yield env.timeout(1)
        S.action.interrupt()
        for state in STATES:
            data[state].append(S.fjoldi[state])
        if showSim:
            d = {"fjöldi á spítala": [S.amount],"capacity":S.cap}
            df = pd.DataFrame(d,index = [i])
            chart.add_rows(df)
            time.sleep(0.1)
        

def sim(showSim,simAttributes):
    #simAttributes inniheldur allar upplýsingar um forsendur hermuninnar
    #Ef maður vill sjá þróun fjölda fólks á spítalanum er showSim = True
    #Skilar núna fjölda á deildum spítalans á hverjum klst.
    TELJA = 0
    env = sp.Environment()
    fjoldi = {
        STATES[0] : 0,
        STATES[1] : 0,
        STATES[2] : 0,
        STATES[3] : 0
    }
    data = {
        STATES[0] : [],
        STATES[1] : [],
        STATES[2] : [],
        STATES[3] : []
    }
    STOP = simAttributes["STOP"]
    print(f"lengd hermunar er {STOP}")
    S = Spitali(fjoldi,env,simAttributes)  # spítali með capacity cap og núverandi sjúklingar á deildum í fjoldi (global breyta)
    print(f"capacity á spítala er {S.cap}")
    if showSim:
        d = {"fjöldi á spítala": [S.amount],"capacity": S.cap}
        df = pd.DataFrame(d,index = [0])
        chart = st.line_chart(df)
        env.process(interrupter(env,S,STOP,data,showSim,chart))
    else:
        env.process(interrupter(env,S,STOP,data,showSim, None))
    env.run(until = STOP)
    print(f"Heildar fjöldi fólks sem kom á spítalann alla hermunina er {TELJA}")
    return data

def flow(deildaskipti): # Fall sem reiknar gögn um flæði sjúklinga á milli deilda
    trans = {}
    stays = {}
    for i in deildaskipti:
        state1,state2 = i
        if state1 != state2:
            if state1 not in trans:
                trans[state1] = {}
            if state2 not in trans[state1]:
                trans[state1][state2] = 0
            trans[state1][state2] += 1
        else:
            if state1 not in stays:
                stays[state1] = 0
            stays[state1] += 1
    
    dlisti = []
    countlisti = []
    # Transitions
    for state1, state2_counts in trans.items():
        for state2, count in state2_counts.items():
            print(f"Farið frá {state1} yfir til {state2}: {count}")
            dlisti.append((state1,state2))
            countlisti.append(count)
    # Stays
    staylisti = []
    count2listi = []
    for state,count in stays.items():
        print(f"Fóru aftur á {state}: {count}")
        staylisti.append((state,state))
        count2listi.append(count)
    countlisti.append(count2listi[0])
    dlisti.append(staylisti[0])
    info1 = dlisti
    info2 = countlisti
    return info1,info2

## Hér kemur streamlit kóðinn

st.title("Hermun heilbrigðiskerfisins")

#sliders o.fl.
with st.expander("Hermunarstillingar"):
    simAttributes["meðalfjöldi"][AGE_GROUPS[0]] = st.number_input("Meðalfjöldi ungra á dag",min_value = 1, max_value=100,
                                                    value = simAttributes["meðalfjöldi"][AGE_GROUPS[0]],step = 1)
    simAttributes["meðalfjöldi"][AGE_GROUPS[1]] = st.number_input("Meðalfjöldi miðaldra á dag",min_value = 1, max_value=100,
                                                    value = simAttributes["meðalfjöldi"][AGE_GROUPS[1]],step = 1)
    simAttributes["meðalfjöldi"][AGE_GROUPS[2]] = st.number_input("Meðalfjöldi aldraðra á dag",min_value = 1, max_value=100,
                                                    value = simAttributes["meðalfjöldi"][AGE_GROUPS[2]],step = 1)
    simAttributes["Upphafslíkur"][0] = st.slider("Líkur á að nýr sjúklingur fari á legudeild", 
                                                    value = simAttributes["Upphafslíkur"][0])
    simAttributes["CAP"] = st.slider("Hámarskfjöldi á spítala",min_value = 100,max_value = 1000,value = 250,step = 50)
    simAttributes["STOP"] = st.number_input("Fjöldi hermunardaga",min_value=10,max_value=1095,value=100)
    L = st.number_input("Fjöldi hermana",5,100,20)

# meðaltími milli koma á spítalann frá mismunandi aldurshópum. Hér höfum við default tímann.
keys = [age_group for age_group in AGE_GROUPS]
vals = [1.0/AGE_GROUP_AMOUNT[age_group] for age_group in AGE_GROUPS]

simAttributes["meðalbið"] = dict(zip(keys,vals))
simAttributes["Upphafslíkur"][1] = 1 - simAttributes["Upphafslíkur"][0]
simAttributes["lambda"] = sum([1.0/simAttributes["meðalbið"][age] for age in AGE_GROUPS])

st.text("Sjá eina hermun með völdum hermunarstillingum")
start = st.button("Start")

flowgogn = np.zeros((20,5))

if start:
   data = sim(True,simAttributes)
   info1,info2 = flow(deildaskipti) # ná í gögn um flæði

st.text("Hermunarstillingar")

totalData = {
    STATES[0] : [],
    STATES[1] : [],
    STATES[2] : [],
    STATES[3] : []
}

hundur = st.button("Byrja hermun!")
if hundur:
    for i in range(L):
        data = sim(False,simAttributes)
        info1,info2 = flow(deildaskipti) # ná í gögn um flæði
        flowgogn[i,:] = info2 # setja í array
        deildaskipti = [] # endurstilla
        for deild in data:
            totalData[deild].append(sum(data[deild])/simAttributes["STOP"])
    for j in range(5):
        info2[j] = np.sum(flowgogn[:,j])/L 

leguData = totalData[STATES[0]]
motData = totalData[STATES[1]]
deadData = totalData[STATES[2]]
homeData = totalData[STATES[3]]

df = pd.DataFrame(
    {
        "Legudeild": leguData,
        "Göngudeild": motData
    }
)
fig = px.box(df)
st.plotly_chart(fig)

# dict sem geymir upplýsingar um flæði sjúklinga
dictf = {
    info1[0] : info2[0],
    info1[1] : info2[1],
    info1[2] : info2[2],
    info1[3] : info2[3],
    info1[4] : info2[4]
}

# Flæðirit sjúklinga á milli deilda
fig2 = go.Figure(go.Sankey(
    arrangement = "snap",
    node = {
        "label": ["Legudeild", "Göngudeild", "Dauði", "Heim", "Spítali"],
        'pad':10},  # 10 Pixels
    link = {
        "source": [0, 0, 0, 1, 1, 4],
        "target": [1, 2, 3, 3, 4, 1],
        "value": [dictf[info1[2]], dictf[info1[3]], dictf[info1[1]], dictf[info1[0]], dictf[info1[4]], dictf[info1[4]]]}))

fig2.update_layout(title_text="Flæði sjúklinga í gegnum kerfið")
st.plotly_chart(fig2)

# Tafla um flæði fyrir L hermanir 
frame = pd.DataFrame(
    flowgogn,
    columns = ("Göngudeild -> Heim","Legudeild -> Heim", "Legudeild -> Göngudeild","Legudeild -> Dauði","Aftur á göngudeild")
)
frame.loc[len(frame.index)] = [dictf[info1[2]], dictf[info1[3]], dictf[info1[1]], dictf[info1[0]], dictf[info1[4]]]
frame = frame.astype("int")

# Highlight-ar seinustu línu dálksins (sem er meðaltal gagna)
df_styled = frame.style.apply(lambda x: ['background-color: yellow' if x.name == len(frame)-1 else '' for i in x], axis=1)

# Sýna töflu
st.dataframe(df_styled)
