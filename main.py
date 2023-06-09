import numpy as np
import random
import time
import pandas as pd
import streamlit as st
import simpy as sp
import plotly.express as px
import plotly.graph_objs as go
import time

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
    STATES[1] : [0.25, 0.0, 0.0, 0.75],
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
            if prev == STATES[0]:
                S.fjoldi[(prev,self.aldur)] -= 1
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
        self.telja = 0
    def patientGen(self,env):
        while True:
            try:
                wait = random.expovariate(self.const["lambda"])
                #print(f"Þurfum að bíða í {wait} langann tíma eftir næsta sjúkling, liðinn tími er {env.now}")
                yield env.timeout(wait)
                aldur = np.random.choice(AGE_GROUPS,p = self.p_age)
                deild = np.random.choice([STATES[0],STATES[1]],p = self.const["Upphafslíkur"])
                p = Patient(aldur,env,deild,self.telja)
                #print(f"Sjúklingur númer {p.numer} fer á {p.deild} og er {p.aldur}, liðinn tími er {env.now}")
                env.process(self.addP(p,False))
            except sp.Interrupt:
                pass
    # Bætum nýjum sjúklingi við á deildina sína og látum hann bíða þar
    def addP(self,p,innritaður):
        if p.deild == STATES[0]:
            self.fjoldi[(p.deild,p.aldur)] += 1
        if not innritaður:
            self.telja += 1
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
        if prev == STATES[0]:
            self.fjoldi[(prev,p.aldur)] -= 1


def interrupter(env,S,STOP,data,showSim,chart):
    for i in range(STOP):
        yield env.timeout(1)
        S.action.interrupt()
        for age_group in AGE_GROUPS:
            data[(STATES[0],age_group)].append(S.fjoldi[(STATES[0],age_group)])
        data["spitaliAmount"].append(S.amount)
        if showSim:
            d = {"fjöldi á spítala": [S.amount],"capacity":S.cap}
            df = pd.DataFrame(d,index = [i])
            chart.add_rows(df)
            time.sleep(0.1)
        

def sim(showSim,simAttributes):
    #simAttributes inniheldur allar upplýsingar um forsendur hermuninnar
    #Ef maður vill sjá þróun fjölda fólks á spítalanum er showSim = True
    #Skilar núna fjölda á deildum spítalans á hverjum klst.
    env = sp.Environment()
    fjoldi = {
        (STATES[0],AGE_GROUPS[0]) : 0,
        (STATES[0],AGE_GROUPS[1]) : 0,
        (STATES[0],AGE_GROUPS[2]) : 0
    }
    data = {
        (STATES[0],AGE_GROUPS[0]) : [],
        (STATES[0],AGE_GROUPS[1]) : [],
        (STATES[0],AGE_GROUPS[2]) : [],
        "spitaliAmount" : []
    }
    STOP = simAttributes["STOP"]
    S = Spitali(fjoldi,env,simAttributes)  # spítali með capacity cap og núverandi sjúklingar á deildum í fjoldi (global breyta)
    if showSim:
        d = {"fjöldi á spítala": [S.amount],"capacity": S.cap}
        df = pd.DataFrame(d,index = [0])
        chart = st.line_chart(df)
        env.process(interrupter(env,S,STOP,data,showSim,chart))
    else:
        env.process(interrupter(env,S,STOP,data,showSim, None))
    env.run(until = STOP)
    print(f"Heildar fjöldi fólks sem kom á spítalann alla hermunina er {S.telja}")
    return data

def hermHundur(start,totalData):
    if start:
        days = simAttributes["STOP"]-1
        mean_stay = [0 for _ in range(days)]
        min_stay = [float("inf") for _ in range(days)]
        max_stay = [0 for _ in range(days)]
        for _ in range(L):
            data = sim(False,simAttributes)
            print(f"lengd data {len(data['spitaliAmount'])}")
            print(f"lengd min og max stay {days}")
            for j in range(days):
                if min_stay[j] > data["spitaliAmount"][j]:
                    min_stay[j] = data["spitaliAmount"][j]
                if max_stay[j] < data["spitaliAmount"][j]:
                    max_stay[j] = data["spitaliAmount"][j]
            for p in data:
                totalData[p].append(np.sum(data[p])/days)
            mean_stay_new = [mean_stay[i] + data["spitaliAmount"][i] for i in range(days)]
            mean_stay = mean_stay_new
        mean_stay_final = [mean_stay[i]/L for i in range(days)]
        totalData["spitaliAmount"] = mean_stay_final

        legudataUngir = totalData[(STATES[0],AGE_GROUPS[0])]
        legudataMid = totalData[(STATES[0],AGE_GROUPS[1])]
        legudataGamlir = totalData[(STATES[0],AGE_GROUPS[2])]
        df = pd.DataFrame(
            {
                "Legudeild ungir": legudataUngir,
                "Legudeild miðaldra": legudataMid,
                "Legudeild Gamlir" : legudataGamlir
            }
        )
        fig1 = px.box(df,labels = {"variable" : "deild", "value" : "meðalfjöldi daga"})
        st.plotly_chart(fig1)
        x = [i for i in range(simAttributes["STOP"])]
        fig2 = go.Figure(
            [
                go.Scatter(
                    x = x,
                    y = totalData["spitaliAmount"],
                    line = dict(color = "rgb(0,100,80)"),
                    mode = "lines"
                ),
                go.Scatter(
                    x = x + x[::-1],
                    y = max_stay + min_stay[::-1],
                    fill = "toself",
                    fillcolor = "rgba(0,100,80,0.2)",
                    line = dict(color = "rgba(255,255,255,0)"),
                    hoverinfo = "skip",
                    showlegend = False
                )
            ]
        )
        st.plotly_chart(fig2)

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
    L = st.number_input("Fjöldi hermana",5,100,100)

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
    (STATES[0],AGE_GROUPS[0]) : [],
    (STATES[0],AGE_GROUPS[1]) : [],
    (STATES[0],AGE_GROUPS[2]) : [],
    "spitaliAmount" : []
}

hundur = st.button("Byrja hermun!")
if hundur:
    with st.spinner("Hermun í gangi..."):
        hermHundur(hundur,totalData)
    st.success("Hermun lokið")


