import numpy as np
import random
import time
import pandas as pd
import streamlit as st
import simpy as sp
import plotly.express as px

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

if start:
   data = sim(True,simAttributes)

st.text("Hermunarstillingar")

totalData = {
    STATES[0] : [],
    STATES[1] : [],
    STATES[2] : [],
    STATES[3] : []
}
hundur = st.button("Byrja hermun!")
if hundur:
    for _ in range(L):
        data = sim(False,simAttributes)
        for deild in data:
            totalData[deild].append(sum(data[deild])/simAttributes["STOP"])

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