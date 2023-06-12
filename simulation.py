import numpy as np
from random import expovariate
from time import sleep
import pandas as pd
import streamlit as st
from simpy import Environment,Interrupt
import plotly.express as px
import plotly.graph_objs as go
from helpers import simAttributes
from itertools import product

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
        new_deild = np.random.choice(S.fastar["Stöður"],p = S.fastar["Færslulíkur"][prev])
        self.deild = new_deild
        S.fjoldi["deildaskipti"][(prev,self.deild)] += 1
        if self.deild == S.fastar["Stöður"][2] or self.deild == S.fastar["Stöður"][3]:
            S.removeP(prev,self)
        else:
            if prev == S.fastar["Stöður"][0]:
                S.fjoldi[self.aldur] -= 1
            yield self.env.process(S.addP(self,True))

class Spitali:
    def __init__(self,fjoldi,env,simAttributes):
        self.fjoldi = fjoldi
        self.env = env
        self.fastar = simAttributes
        self.cap = self.fastar["CAP"]
        self.p_age = [(1.0/self.fastar["meðalbið"][age])/self.fastar["lambda"] for age in self.fastar["Aldurshópar"]]
        self.telja = 0
        self.amount = 0 #sum(list(fjoldi.values()))
        self.action = env.process(self.patientGen(env))
    def patientGen(self,env):
        while True:
            try:
                wait = expovariate(self.fastar["lambda"])
                #print(f"Þurfum að bíða í {wait} langann tíma eftir næsta sjúkling, liðinn tími er {env.now}")
                yield env.timeout(wait)
                aldur = np.random.choice(self.fastar["Aldurshópar"],p = self.p_age)
                deild = np.random.choice([self.fastar["Stöður"][0],self.fastar["Stöður"][1]],p = self.fastar["Upphafslíkur"])
                p = Patient(aldur,env,deild,self.telja)
                #print(f"Sjúklingur númer {p.numer} fer á {p.deild} og er {p.aldur}, liðinn tími er {env.now}")
                env.process(self.addP(p,False))
            except Interrupt:
                pass
    # Bætum nýjum sjúklingi við á deildina sína og látum hann bíða þar
    def addP(self,p,innritaður):
        if p.deild == self.fastar["Stöður"][0]:
            self.fjoldi[p.aldur] += 1
        if not innritaður:
            self.telja += 1
            self.amount += 1
            #print(f"fjöldi á spítala er núna {self.amount}, liðinn tími er {self.env.now}")
        wait = expovariate(1.0/self.fastar["Biðtímar"][(p.aldur,p.deild)])
        #print(f"Sjúklingur númer {p.numer} á {p.deild} þarf að bíða þar í {wait}, liðinn tími er {self.env.now}")
        yield self.env.timeout(wait)
        yield self.env.process(p.updatePatient(self))
    # fjarlægjum sjúkling af deildinni prev
    def removeP(self,prev,p):
        #print(f"Sjúklingur númer {p.numer} fer af {prev} til {p.deild}, liðinn tími er {self.env.now}")
        self.amount -= 1
        if prev == self.fastar["Stöður"][0]:
            self.fjoldi[p.aldur] -= 1


def interrupter(env,S,STOP,data,showSim,chart):
    for i in range(STOP):
        yield env.timeout(1)
        S.action.interrupt()
        for age_group in S.fastar["Aldurshópar"]:
            data[age_group].append(S.fjoldi[age_group])
        data["spitaliAmount"].append(S.amount)
        if showSim:
            d = {"fjöldi á spítala": [S.amount],"capacity":S.cap}
            df = pd.DataFrame(d,index = [i])
            chart.add_rows(df)
            sleep(0.1)

"""PROB = {
    STATES[0] : [0.0, 0.3, 0.1, 0.6],
    STATES[1] : [0.25, 0.0, 0.0, 0.75],
    STATES[2] : [0.0, 0.0, 1.0, 0.0],
    STATES[3] : [0.0, 0.0, 0.0, 1.0]
}"""

def sim(showSim,simAttributes):
    #simAttributes inniheldur allar upplýsingar um forsendur hermuninnar
    #Ef maður vill sjá þróun fjölda fólks á spítalanum er showSim = True
    #Skilar núna fjölda á deildum spítalans á hverri klst og upplýsingar um hvert fólk fór innan spítalans.
    env = Environment()
    skiptiKeys = []
    n = len(simAttributes["Stöður"])
    for tvennd in product(simAttributes["Stöður"],range(n)):
        if simAttributes["Færslulíkur"][tvennd[0]][tvennd[1]] > 0.0:
            skiptiKeys.append((tvennd[0],simAttributes["Stöður"][tvennd[1]]))
    deildaskipti = {keys : 0 for keys in skiptiKeys}
    fjoldi = {
        simAttributes["Aldurshópar"][0] : 0,
        simAttributes["Aldurshópar"][1] : 0,
        simAttributes["Aldurshópar"][2] : 0,
        "deildaskipti" : deildaskipti
    }
    data = {
        simAttributes["Aldurshópar"][0] : [],
        simAttributes["Aldurshópar"][1] : [],
        simAttributes["Aldurshópar"][2] : [],
        "spitaliAmount" : [],
        "deildaskipti" : {}
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
    data["deildaskipti"] = S.fjoldi["deildaskipti"]
    print(f"Heildar fjöldi fólks sem kom á spítalann alla hermunina er {S.telja}")
    return data

def hermHundur(start,totalData,simAttributes):
    L = simAttributes["Fjöldi hermana"]
    if start:
        days = simAttributes["STOP"]-1
        stayData = []
        for _ in range(L):
            data = sim(False,simAttributes)
            stayData.append(data["spitaliAmount"])
            for key in simAttributes["Aldurshópar"]:
                totalData[key].append(np.sum(data[key])/days)
            #print(f"lengd data {len(data['spitaliAmount'])}")
            #print(f"lengd min og max stay {days}")
        stayData_arr = np.array(stayData)
        stayData_arr = np.transpose(stayData_arr)
        #print(stayData_arr)
        #print(np.shape(stayData_arr))
        mean_stay = [np.sum(stayData_arr[row,:])/L for row in range(days)]
        max_stay = [np.amax(stayData_arr[row,:]) for row in range(days)]
        min_stay = [np.amin(stayData_arr[row,:]) for row in range(days)]
        legudataUngir = totalData[simAttributes["Aldurshópar"][0]]
        legudataMid = totalData[simAttributes["Aldurshópar"][1]]
        legudataGamlir = totalData[simAttributes["Aldurshópar"][2]]
        df = pd.DataFrame(
            {
                "Legudeild ungir": legudataUngir,
                "Legudeild miðaldra": legudataMid,
                "Legudeild Gamlir" : legudataGamlir
            }
        )
        fig1 = px.box(df,labels = {"variable" : "deild", "value" : "meðalfjöldi daga"})
        st.plotly_chart(fig1)
        st.text(f"Hér sést meðalfjöldi innlagna á dag yfir þessar {L} hermanir.")
        x = [i for i in range(days)]
        fig2 = go.Figure(
            [
                go.Scatter(
                    x = x,
                    y = mean_stay,
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
        fig2.update_layout(
            xaxis_title = "Dagar",
            yaxis_title = "meðalfjöldi"
        )
        st.plotly_chart(fig2)
        keyList = list(data["deildaskipti"].keys())
        nodeNum = {simAttributes["Stöður"][i] : i for i in range(len(simAttributes["Stöður"]))}
        source = []
        target = []
        for tvennd in keyList:
            source.append(nodeNum[tvennd[0]])
            target.append(nodeNum[tvennd[1]])
        print(simAttributes["Stöður"])
        print(source)
        print(target)
        data_graph = [data["deildaskipti"][tvennd] for tvennd in list(data["deildaskipti"].keys())]
        print(data_graph)
        fig3 = go.Figure(go.Sankey(
        arrangement = "snap",
        node = {
            "label": simAttributes["Stöður"],
            'pad':10},
        link = {
            "arrowlen" : 10,
            "source" : source,
            "target" : target,
            "value" : data_graph}))
        fig3.update_layout(title_text="Flæði sjúklinga í gegnum kerfið")
        st.plotly_chart(fig3)
