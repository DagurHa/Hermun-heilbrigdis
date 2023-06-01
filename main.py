import numpy as np
import random
import time
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import simpy as sp

SEED = 100
TIMI = 0
STOP = 10000
MEAN_VISIT = [5.0,1.0]
MEAN_TIME = [9.0,5.0]

random.seed(SEED)

class Patient:
    def __init__(self,env,aldur):
        self.aldur = aldur
        self.env = env
    
def patient_gen(env):
    s = MEAN_VISIT[0] + MEAN_VISIT[1]
    vis = random.expovariate(1.0/s)
    yield env.timeout(vis)
    r = random.random()
    if r < MEAN_VISIT[0]/s:
        age = random.randint(65,99)
        p = Patient(env,age)
        print("Nú kom gömul manneskja á tímanum",env.now)
        return p
    else:
        age = random.randint(0,64)
        p = Patient(env,age)
        print("Nú kom ung manneskja á tímanum",env.now)
        return p

def get_patient(env):
    patient = yield env.process(patient_gen(env))
    return patient

class Spitali:
    def __init__(self,env,amount):
        self.amount = amount
        self.env = env
    def newP(self,p,env):
        self.amount += 1
        if p.aldur < 65:    
            wait = random.expovariate(1.0/MEAN_TIME[0])
        else:
            wait = random.expovariate(1.0/MEAN_TIME[1])
        yield env.timeout(wait)
        if p.aldur < 65:
            print(f"Ung manneskja útskrifast á tímanum {env.now}")
        else:
            print(f"Gömul manneskja útskrifast á tímanum {env.now}")
        self.amount -= 1

def sim(env):
    S = Spitali(env,0)
    while True:
        s = MEAN_VISIT[0] + MEAN_VISIT[1]
        vis = random.expovariate(1.0/s)
        yield env.timeout(vis)
        r = random.random()
        if r < MEAN_VISIT[0]/s:
            age = random.randint(65,99)
            p = Patient(env,age)
            print("Nú kom gömul manneskja á tímanum",env.now)
        else:
            age = random.randint(0,64)
            p = Patient(env,age)
            print("Nú kom ung manneskja á tímanum",env.now)
        #env.process(S.newP(p,env))
        


env = sp.Environment()
env.process(sim(env))
env.run(until = 90)

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

st.write("Hermunarstillingar")

dt = st.slider("Fjöldi daga per hermun",10,10000,1000,100)
L = st.number_input("Fjöldi hermana",1,1000,1)
p = [PROB_A,PROB_U]
