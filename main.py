import simpy as sp
import streamlit as st
import numpy as np
import math
import random
import time
import os
import signal
from multiprocessing import Process
import pandas as pd
import matplotlib.pyplot as plt

TIMI = 0
STOP = 10000
prob = {
    "surgery" : (0.0,0.7,0.3,0.0),
    "móttaka" : (0.5,0.0,0.0,0.5),
    "death" : (0.0,0.0,1.0,0.0),
    "Heim" : (0.0,0.0,0.0,1.0)
}

class Patient:
    def __init__(self,aldur,place):
        self.aldur = aldur
        self.place = place
        if self.place == "skurðaaðgerð":
            self.p_death = 0.3
            self.p_surgery = 0.0
            self.p_mottaka = 0.7
        if self.place == "móttaka":
            self.p_death = 0.0
            self.p_surgery = 0.3
            self.p_home = 0.7

class Spitali:
    def __init__(self,cap,amount):
        self.cap = cap
        self.amount = amount
    def addP(self):
        #if self.amount == self.cap:
            #raise Exception("Nú er spítalinn fullur það tók")
        self.amount += 1
    def removeP(self):
        self.amount -= 1

def transition(p,r,P,S,n):
    if p.place == "móttaka":
        if r < p.p_death:
            P.remove(p)
            S.removeP()
        if r >= p.p_death and r <= p.p_surgery:
            P.remove(p)
            S.removeP()
            n += 1
        else:
            p.place = "skurðaaðgerð"
    elif p.place == "skurðaaðgerð":
        if r < p.p_surgery:
            p.place = "skurðaaðgerð"
        if r >= p.p_surgery and r <= p.p_death:
            P.remove(p)
            S.removeP()
        else:
            p.place = "móttaka"

def sim(stop):
    p_A = PROB_A
    p_U = PROB_U
    n = N
    timi = TIMI
    t = T
    cap = CAP
    P = []              # listi af sjúklingum á spítala
    S = Spitali(cap,0)  # spítali með capacity 500 og núverandi sjúklinga 0
    d = {"fjöldi á spítala":[0],"capacity":cap}
    df = pd.DataFrame(d,index = [timi])
    chart = chart_col.line_chart(df)
    while(timi < stop):
        timi += t
        for _ in range(t):
            s_A = np.random.binomial(h_A*n,p_A)
            s_U = np.random.binomial(h_U*n,p_U)
            n -= (s_A+s_U)
            for _ in range(s_A):
                age = random.randint(65,99)
                pi = Patient(age,"móttaka")
                P.append(pi)
                S.addP()
            for _ in range(s_U):
                age = random.randint(1,64)
                pi = Patient(age,"móttaka")
                P.append(pi)
                S.addP()
            for p in P:
                r = random.random()
                transition(p,r,P,S,n)
        d = {"fjöldi á spítala": [S.amount],"capacity":cap}
        df = pd.DataFrame(d,index = [timi])
        chart.add_rows(df)

#sliders o.fl.
with st.expander("Breyta hlutum"):
    h_A = st.slider("Hlutfall aldraðra",value = 0.3,step = 0.02)
    N = st.slider("Stærð þjóðar",min_value = 500,max_value = 5000,value = 1000,step = 100)
    T = st.slider("Tímaskref í dögum",min_value = 1,max_value = 30,step = 1)
    CAP = st.slider("Hámarskfjöldi á spítala",min_value = 100,max_value = 1000,value = 250,step = 50)
    PROB_A = st.slider("Líkur á að aldraðir fari á spítala",value = 0.1,step=0.01)
    PROB_U = st.slider("Líkur á að ungir fari á spítala",value = 0.02,step=0.01)

h_U = 1-h_A

visual_col,chart_col = st.columns(2)

labels = "Aldraðir","Ungir"
sizes = [h_A*N,h_U*N]

fig1,ax1 = plt.subplots()
ax1.pie(sizes,labels = labels)

visual_col.pyplot(fig1)

start = chart_col.button("Start")
stop = chart_col.button("Stop")

if start:
    sim(STOP)
    time.sleep(0.1)

if stop:
    st.stop()

st.write("Hermunarstillingar")

dt = st.slider("Fjöldi daga per hermun",10,10000,1000,100)
L = st.number_input("Fjöldi hermana",1,1000,1)


