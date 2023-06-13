from time import time
import streamlit as st
from helpers import *
from simulation import sim,hermHundur
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import numpy as np

## Hér kemur streamlit kóðinn

#Athuga gæti verið gott að setja default sim attributes lika

start_time = time()
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
    simAttributes["Fjöldi hermana"] = st.number_input("Fjöldi hermana",5,100,20)

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
    AGE_GROUPS[0] : [],
    AGE_GROUPS[1] : [],
    AGE_GROUPS[2] : [],
    "spitaliAmount" : [],
    "meðal lega" : [],
    "mesta lega" : [],
    "minnsta lega" : [],
    "Sankey" : {},
    "dagar yfir cap" : []
}

hundur = st.button("Byrja hermun!")
if hundur:
    with st.spinner("Hermun í gangi..."):
        totalData = hermHundur(hundur,totalData,simAttributes)
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
        fig1 = px.box(df,labels = {"variable" : "Deild", "value" : "Meðalfjöldi daga"},title = "Dreifing aldurshópa á legudeild")
        st.plotly_chart(fig1)
        st.text(f"Hér sést meðalfjöldi innlagna á dag yfir þessar {L} hermanir.")
        days = simAttributes["STOP"] -1
        mean_stay = totalData["meðal lega"]
        min_stay = totalData["minnsta lega"]
        max_stay = totalData["mesta lega"]
        x = [i for i in range(days)]
        fig2 = go.Figure(
            [
                go.Scatter(
                    x = x,
                    y = mean_stay,
                    line = dict(color = "rgb(0,100,80)"),
                    mode = "lines",
                    name = "Meðal"
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
        fig2.update_traces(marker=dict(size=24, color="blue"), selector = dict(name="first_trace"))
        fig2.update_layout(
            title = "Innlagnir",
            xaxis_title = "Dagar",
            yaxis_title = "Meðalfjöldi"
        )
        st.plotly_chart(fig2)
        sankeyData = totalData["Sankey"]
        nodeNum = {simAttributes["Stöður"][i] : i for i in range(len(simAttributes["Stöður"]))}
        source = []
        target = []
        for tvennd in simAttributes["deildaskipti"]:
            source.append(nodeNum[tvennd[0]])
            target.append(nodeNum[tvennd[1]])
        print(simAttributes["Stöður"])
        print(source)
        print(target)
        data_graph = [np.sum(sankeyData[key])/L for key in simAttributes["deildaskipti"]]
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
        meanYfirCap = np.sum(totalData["dagar yfir cap"])/L
        st.plotly_chart(fig3)
        st.write(f"Meðalfjöldi daga sem sjúklingar á spítala voru yfir hámarki: {meanYfirCap}")
    st.success("Hermun lokið")
print(time()-start_time)