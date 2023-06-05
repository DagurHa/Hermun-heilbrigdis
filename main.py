import numpy as np
import random
import time
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from bokeh.plotting import figure,show
from bokeh.io import output_notebook

TIMI = 0
STOP = 10000
prob = {
    "legudeild" : [0.0, 0.7, 0.3, 0.0],
    "móttaka" : [0.5, 0.0, 0.0, 0.5],
    "death" : [0.0, 0.0, 1.0, 0.0],
    "Heim" : [0.0, 0.0, 0.0, 1.0]
}
#Athuga gæti verið gott að setja default sim attributes lika
simAttributes = {}

class Patient:
    def __init__(self,aldur,place):
        self.aldur = aldur
        self.place = place
        self.timiSpitala = 0
        self.attribs = prob
    def updatePatient(self,S):
        assert self.place in self.attribs, "sjúklingur er ekki á vel skilgreindum stað"
        prev = self.place
        for deild in self.attribs:
            if self.place == deild:
                self.place = np.random.choice(list(self.attribs.keys()), p = self.attribs[deild])
        if self.place != "Heim" and self.place != "death":
            S.moveP(self.place,prev)

class Spitali:
    def __init__(self,cap,fjoldi):
        self.cap = cap
        self.fjoldi = fjoldi
        self.amount = sum(list(fjoldi.values()))
    def addP(self,p):
        self.fjoldi[p.place] += 1
        self.amount += 1
    def removeP(self):
        self.amount -= 1
    def moveP(self,new,prev):
        self.fjoldi[new] += 1
        self.fjoldi[prev] -= 1
 
def sim(showSim,simAttributes):
    #simAttributes inniheldur allar upplýsingar um forsendum hermuninnar
    #Ef maður vill sjá þróun fjölda fólks á spítalanum er showSim = True
    #Skilar núna fjölda á deildum spítalans á hverju dt skrefi.
    fjoldi = {
    "legudeild" : 0,
    "móttaka" : 0
    }
    data = {
        "legudeild" : [],
        "móttaka" : []
    }
    p_A = simAttributes["p_A"]
    p_U = simAttributes["p_U"]
    dt = simAttributes["dt"]
    N = simAttributes["N"]
    h_A = simAttributes["h_A"]
    h_U = simAttributes["h_U"]
    timi = TIMI #global breyta
    cap = simAttributes["CAP"]
    STOP = simAttributes["STOP"]
    P = []            # listi sjúklinga á spítala
    S = Spitali(cap,fjoldi)  # spítali með capacity cap og núverandi sjúklingar á deildum í fjoldi (global breyta)
    if showSim:
        d = {"fjöldi á spítala":[0],"capacity":cap}
        df = pd.DataFrame(d,index = [timi])
        chart = chart_col.line_chart(df)
    for deild in S.fjoldi:
        data[deild].append(S.fjoldi[deild])
    while(timi < STOP):
        timi += dt
        for _ in range(dt):
            s_A = np.random.binomial(h_A*N,p_A)
            s_U = np.random.binomial(h_U*N,p_U)
            N -= (s_A+s_U)
            for _ in range(s_A):
                age = random.randint(65,99)
                pi = Patient(age,"móttaka")
                P.append(pi)
                S.addP(pi)
            for _ in range(s_U):
                age = random.randint(1,64)
                pi = Patient(age,"móttaka")
                P.append(pi)
                S.addP(pi)
            for p in P:
                p.updatePatient(S)
                if p.place == "Death":
                    P.remove(p)
                    S.removeP()
                if p.place == "Heim":
                    P.remove(p)
                    S.removeP()
                    N+=1
        if showSim:            
            d = {"fjöldi á spítala": [S.amount],"capacity":cap}
            df = pd.DataFrame(d,index = [timi])
            chart.add_rows(df)
            time.sleep(0.1)
        for deild in S.fjoldi:
            data[deild].append(S.fjoldi[deild])
        #print("fjöldi fólks á spítala á degi",timi,"er",S.amount)
    return data

#sliders o.fl.
with st.expander("Hermunarstillingar"):
    simAttributes["h_A"] = st.slider("Hlutfall aldraðra",value = 0.3,step = 0.02)
    simAttributes["N"] = st.number_input("Stærð þjóðar",min_value = 500,max_value = 10000,value = 1000)
    simAttributes["dt"] = st.slider("Tímaskref í dögum",min_value = 1,max_value = 30,step = 1)
    simAttributes["CAP"] = st.slider("Hámarskfjöldi á spítala",min_value = 100,max_value = 1000,value = 250,step = 50)
    simAttributes["p_A"] = st.slider("Líkur á að aldraðir fari á spítala á dag",value = 0.1,step=0.1)
    simAttributes["p_U"] = st.slider("Líkur á að ungir fari á spítala á dag",value = 0.02,step=0.1)
    simAttributes["STOP"] = st.number_input("Fjöldi hermunardaga",min_value=10,max_value=1095,value=100)

simAttributes["h_U"] = 1-simAttributes["h_A"]

visual_col,chart_col = st.columns(2)

labels = "Aldraðir","Ungir"
sizes = [simAttributes["h_A"]*simAttributes["N"],simAttributes["h_U"]*simAttributes["N"]]

fig1,ax1 = plt.subplots()
ax1.pie(sizes,labels = labels)

visual_col.pyplot(fig1)

chart_col.write("Sjá hermun með völdum hermunarstillingum")
start = chart_col.button("Start")
stop = chart_col.button("Stop")

if start:
   data = sim(True,simAttributes)

if stop:
    st.stop()

st.write("Hermunarstillingar")

L = st.number_input("Fjöldi hermana",2,1000,100)

totalData = {
    "legudeild" :[] ,
    "móttaka" : []
}
hundur = st.button("Byrja hermun!")
if hundur:
    for _ in range(L):
        data = sim(False,simAttributes)
        print(data)
        for deild in data:
            totalData[deild].append(sum(data[deild])/simAttributes["STOP"])

leguData = totalData["legudeild"]
motData = totalData["móttaka"]

print(totalData)

fig2, ax2 = plt.subplots()
ax2.boxplot([leguData,motData])

st.pyplot(fig2)

"""gamall = 0
ungur = 0
for p in patients:
    if p.check_in_time and p.check_out_time is not None:    
        stay.append(p.check_out_time - p.check_in_time)
    if p.aldur < 65:
        ungur +=1
    else:
        gamall +=1

print(f"Number of patients: {gamall+ungur}")
print(f"Number of patients that have yet to check out: {noncheckout}")
print(f"Average stay of patients: {sum(stay)/len(stay)} time units")
print(f"Fraction of old people: {gamall/(gamall+ungur)}")

plot = figure(x_range=['Younger than 65', 'Older than 65'], title='Patient Age Distribution')

Creating a histogram
plot.vbar(x=['Younger than 65', 'Older than 65'], top=[ungur, gamall], width=0.4)

Styling the plot
plot.xaxis.axis_label = 'Age Group'
plot.yaxis.axis_label = 'Number of Patients'

Show the plot
st.write(plot)"""
