import numpy as np
import random
import time
import pandas as pd
import streamlit as st
import simpy as sp
import plotly.express as px

TIMI = 0  #Byrjunartími hermunar (gæti verið useless)
#Hér eftir koma allar global breytur.
# Mismunandi stöður sjúklings. Bætum við og breytum þegar lengra er komið.
STATES = ["legudeild", "göngudeild", "dauði", "heim"]
AGE_GROUPS = ["Ungur","Miðaldra","Gamall"] # mismunandi aldurshópar sjúklings. Breytum/bætum við mögulega
# meðaltími milli koma á spítalann frá mismunandi aldurshópum. Hér höfum við default tímann.
# Þessi tími mun vera byggður á gögnum vonandi, síðan er hægt að breyta í streamlit til að fá mismunandi útkomur.
ARRIVAL_RATES = {
    AGE_GROUPS[0] : 1.0,
    AGE_GROUPS[1] : 0.8,
    AGE_GROUPS[2] : 0.5
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
    "Komutímar" : ARRIVAL_RATES,
    "Færslulíkur" : PROB,
    "Upphafslíkur" : INITIAL_PROB
}

class Patient:
    def __init__(self,aldur,env,deild):
        self.deild = deild
        self.env = env
        self.aldur = aldur
        self.timiSpitala = 0 # Þetta gæti verið gott í framtíð
        self.attribs = PROB
    # Þegar sjúklingur er búinn á sinni deild finnum við hvert hann fer næst og sendum hann þangað
    def updatePatient(self,S):
        prev = self.deild
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
        self.p_age = [(1.0/self.const["Komutímar"][age])/self.const["lambda"] for age in AGE_GROUPS]
        self.env = env
        self.cap = self.const["STOP"]
        self.fjoldi = fjoldi
        self.amount = 0 # sum(list(fjoldi.values()))
        self.action = env.process(self.patientGen(env))
    def patientGen(self,env):
        while True:
            try:
                wait = random.expovariate(self.const["lambda"])
                yield env.timeout(wait)
                aldur = np.random.choice(AGE_GROUPS,p = self.p_age)
                deild = np.random.choice([STATES[0],STATES[1]],p = INITIAL_PROB)
                p = Patient(aldur,env,deild)
                yield env.process(self.addP(p,False))
            except sp.Interrupt:
                pass
    # Bætum nýjum sjúklingi við á deildina sína og látum hann bíða þar
    def addP(self,p,innritaður):
        self.fjoldi[p.deild] += 1
        if not innritaður:
            self.amount += 1
        wait = random.expovariate(1.0/MEAN_WAIT_TIMES[(p.aldur,p.deild)])
        yield self.env.timeout(wait)
        yield self.env.process(p.updatePatient(self))
    # fjarlægjum sjúkling af deildinni prev
    def removeP(self,prev,p):
        self.amount -= 1
        self.fjoldi[prev] -= 1
        self.fjoldi[p.deild] += 1 # Ef sjúklingur er farinn af spítala er hann annað hvort dáinn eða farinn heim núna


def interrupter(env,S,t,data,showSim,chart):
    wait_time = t/100.0
    for i in range(t):
        yield env.timeout(wait_time)
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
    S = Spitali(fjoldi,env,simAttributes)  # spítali með capacity cap og núverandi sjúklingar á deildum í fjoldi (global breyta)
    if showSim:
        d = {"fjöldi á spítala": [S.amount],"capacity": S.cap}
        df = pd.DataFrame(d,index = [0])
        chart = st.line_chart(df)
        env.process(interrupter(env,S,STOP,data,showSim,chart))
    else:
        env.process(interrupter(env,S,STOP,data,showSim, None))
    env.run(until = STOP)
    return data


## Hér kemur streamlit kóðinn

st.title("Hermun heilbrigðiskerfisins")

#sliders o.fl.
with st.expander("Hermunarstillingar"):
    simAttributes["Komutímar"][AGE_GROUPS[0]] = st.number_input("Meðaltími milli komu ungra",min_value = 0.01, max_value=5.0,
                                                    value = simAttributes["Komutímar"][AGE_GROUPS[0]],step = 0.02)
    simAttributes["Komutímar"][AGE_GROUPS[1]] = st.number_input("Meðaltími milli komu miðaldra",min_value = 0.01, max_value=5.0,
                                                    value = simAttributes["Komutímar"][AGE_GROUPS[1]],step = 0.02)
    simAttributes["Komutímar"][AGE_GROUPS[2]] = st.number_input("Meðaltími milli komu aldraðra",min_value = 0.01, max_value=5.0,
                                                    value = simAttributes["Komutímar"][AGE_GROUPS[2]],step = 0.02)
    simAttributes["Upphafslíkur"][0] = st.slider("Líkur á að nýr sjúklingur fari á legudeild", 
                                                    value = simAttributes["Upphafslíkur"][0])
    simAttributes["CAP"] = st.slider("Hámarskfjöldi á spítala",min_value = 100,max_value = 1000,value = 250,step = 50)
    simAttributes["STOP"] = st.number_input("Fjöldi hermunardaga",min_value=10,max_value=1095,value=100)
    L = st.number_input("Fjöldi hermana",100,1000,100)

simAttributes["Upphafslíkur"][1] = 1 - simAttributes["Upphafslíkur"][0]
simAttributes["lambda"] = sum([1.0/ARRIVAL_RATES[age] for age in AGE_GROUPS])

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
        print(data)
        for deild in data:
            totalData[deild].append(sum(data[deild])/simAttributes["STOP"])

leguData = totalData[STATES[0]]
motData = totalData[STATES[1]]

print(totalData)
print(len(totalData["legudeild"]))

df = pd.DataFrame(
    {"Legudeild": leguData,
     "Göngudeild": motData}
)
fig = px.box(df)
st.plotly_chart(fig)


