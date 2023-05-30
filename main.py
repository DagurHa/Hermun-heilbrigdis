import numpy as np
import random
import time
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import simpy as sp

TIMI = 0
STOP = 10000
MEAN_VISIT = [20.0,5.0] #1.0 deilt með þessu fyrir expovar
MEAN_STAY_LEGA = [5.0,2.0]
MEAN_STAY_MOT = 0.2

class Patient:
    def __init__(env,self,aldur,id):
        self.aldur = aldur
        self.env = env
        self.id = id
    
def patient_gen(env):
    s = MEAN_VISIT[0] + MEAN_VISIT[1]
    vis = random.expovariate(1.0/s)
    yield vis
    r = random.random()
    if r < MEAN_VISIT[0]/s:
        age = random.randint(65,99)
        p = Patient(env,age,env.now)
        return p
    else:
        age = random.randint(0,64)
        p = Patient(env,age,env.now)

class Spitali:
    def __init__(self,env,amount,inn_cap,mottaka_cap):
        self.inn_cap = inn_cap
        self.amount = amount
        self.env = env
        self.mottaka_cap = mottaka_cap
        self.mottaka = sp.Resource(env,mottaka_cap)
        self.inn = sp.Resource(env,inn_cap)
    def newP(p,self,env):
        with self.mottaka.request() as req:
            amount += 1
            yield req
            wait_time = random.expovariate(1.0/MEAN_STAY_MOT)
            yield env.timeout(env,wait_time)
            self.mottaka.release(req)
            r = random.random() # Hvort göngu eða legu
            self.newInn(p,r,env,self.inn)
    def newInn(p,r,env,inn):
        if r < 0.7:
            lam = 3
        else:
            lam = 10
        with inn.request() as req:
            yield req
            stay_time = random.expovariate(1.0/lam)
            yield env.timeout(env,stay_time)
            inn.release(req)
            amount -= 1

def sim(stop,p_S,N,T):
    env = sp.Environment()
    S = Spitali(env,0,40,3)
    
    p = patient_gen(env)
    S.newP(env,p)


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

for _ in range(L):
    sim(dt,p,N,T)