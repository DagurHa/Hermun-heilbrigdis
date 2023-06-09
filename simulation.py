import numpy as np
import random
import time
import pandas as pd
import streamlit as st
import simpy as sp
import plotly.express as px
import plotly.graph_objs as go
from helpers import *

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
        x = [i for i in range(days)]
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