import random
import simpy as sp
import numpy as np
import streamlit as st

SEED = 27
random.seed(27)
AGE_GROUPS = ["Ungir","Miðaldra","Gamlir"]
#meðaltöl aldurshópa, fyrsta tala er meðaltími þar til aðili kemur á spítala,
#tala tvö er meðal bið á göngudeild, þriðja er meðal bið á legudeild
MEANS_ungir = [4.0, 5.0, 40.0] 
MEANS_midaldra = [2.0,10.0,50.0]
MEANS_gamlir = [1.0,15.0,60.0]
TOTAL_DATA = {
        "Legustaða:" : [],
        "Göngustaða" : [],
        "Heildarfjöldi" : []
    }

#Líkur fyrir aldurshópa að ferðast milli eininga í spítala
#nú höfum við þrjár einingar: göngudeild, legudeild og móttaka
#Gerum ráð fyrir að sjúklingur sé engann tíma í móttöku 
transProb = {
    "Ungur": [0.7,0.3],
    "Miðaldra": [0.3,0.7],
    "Gamall": [0.1,0.9]
}
age_group_attribs = {
    "Ungur": [4.0, 5.0, 40.0],
    "Miðaldra": [2.0, 10.0, 50.0],
    "Gamall": [1.0, 15.0, 60.0]
}

class Patient:
    def __init__(self,env,age,innrita):
        self.env = env
        self.age = age
        self.innrit = innrita
    #Finnum eiginleika sjúklings miðað við aldur
    def age_attribs(self,age_group_attribs):
        return age_group_attribs[self.age]
    #Finnum færslulíkur innan kerfis
    def trans_prob(self,transProb):
        return transProb[self.age]

class Spitali:
    #Spítali með upphafsfjölda: amount
    def __init__(self,env,amount = 0,g_deild_amount = 0,l_deild_amount = 0):
        self.env = env
        self.amount = amount
        self.g_deild_amount = g_deild_amount
        self.l_deild_amount = l_deild_amount
    #Ný sjúklingur í móttöku
    def m_deildNyrPatient(self,env,p):
        #ef sjúklingur er nýr þá fer hann á einhvern stað
        if p.innrita:
            self.amount += 1 
            r = random.random()
            if r < p.trans_prob(transProb)[0]:
                env.process(self.g_deildNyrPatient(env,p))
            else:
                env.process(self.l_deildNyrPatient(env,p))  
        else:
            self.returnHome(p)
    #Nýr sjúklingur á göngudeild
    def g_deildNyrPatient(self,env,p):
        self.g_deild_amount += 1
        p.innrita = False
        stay_t = random.expovariate(1.0/p.attribs[1])
        yield env.timeout(stay_t)
        self.g_deild_amount -= 1
        env.process(self.m_deildNyrPatient(env,p))
    #Nýr sjúklingur á legudeild
    def l_deildNyrPatient(self,env,p):
        self.l_deild_amount += 1
        p.innrita = False
        stay_t = random.expovariate(1.0/p.attribs[2])
        yield env.timeout(stay_t)
        self.l_deild_amount -= 1
        env.process(self.m_deildNyrPatient(env,p))
    #Sjúklingur fer heim
    def returnHome(self,p):
        self.amount -= 1

def patientGen(env,s,S,age_group,lambd):
    wait = random.expovariate(s)
    yield env.timeout(wait)
    age = np.random.choice(age_group,p=lambd)
    p = Patient(env,age,True)
    env.process(S.m_deildNyrPatient(env,p))

#Athugum stöðu spítalans á t tíma fresti (setjum klukkutima default)
def monitor(S,env,t):
    yield env.timeout(t)
    data = {
        "Legustaða": S.l_deild_amount,
        "Göngustaða": S.g_deild_amount,
        "Heildarfjöldi": S.amount
    }
    return data

#Skrítnar leiðir til að safna gögnum
def get_data(S,env,t=1):
    data = yield env.process(monitor(S,env,t))
    return data

def collectData(data):
    for deild in data:
            TOTAL_DATA[deild].append(data[deild])
    print(TOTAL_DATA)

outer_env = sp.Environment()

def sim(T):
    env = sp.Environment()
    print("byrja")
    t = 24*T
    lambd = []
    #Gerum lista af stikunum
    for age_group in age_group_attribs:
        lambd.append(1.0/age_group_attribs[age_group][0])
    #Þetta verður stikinn í exp dreifingunni, min af exp dreifingum er exp dreifing af summu stikanna
    s = sum(lambd)
    S = Spitali(env,0)
    env.run(until = t)
    while True:
        env.process(patientGen(env,s,S,age_group,lambd))

p = outer_env.process(sim(7))
outer_env.run(until = p)
