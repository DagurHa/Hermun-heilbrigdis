from time import time
import streamlit as st
from helpers import *
from simulation import sim,hermHundur
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import cProfile
import pstats
import io
from copy import copy,deepcopy
from math import ceil

## Hér kemur streamlit kóðinn

#Athuga gæti verið gott að setja default sim attributes lika

start_time = time()
st.title("Hermun heilbrigðiskerfisins")

st.header("Deildir")

gongu,legu = st.tabs(["Göngudeild","Legudeild"])

with gongu:
    st.write("Veldu hversu marga sjúklinga hver göngudeildalæknir getur séð um á dag.")
    simAttributes["Starfsþörf"][("göngudeild","Læknar")][0] = st.number_input("Fjöldi",value = STARFSDEMAND[("göngudeild","Læknar")][0],max_value=40,step =1)
    st.write("Veldu hversu marga sjúklinga hver göngudeildar hjúkrunarfræðingur getur séð um á dag.")
    simAttributes["Starfsþörf"][("göngudeild","Hjúkrunarfræðingar")][0] = st.number_input("Fjöldi",value = STARFSDEMAND[("göngudeild","Hjúkrunarfræðingar")][0],max_value=40,step =1,key = 123)

with legu:
    st.write("Veldu fjölda lækna á legudeild,")
    SERF = st.number_input("Sérfræðingur", value = 1)
    SNL = st.number_input("Sérnámslæknir", value = 1)
    SGL = st.number_input("Deildarlæknir",value = 1)
    st.write("Veldu legurými á einni legudeild.")
    simAttributes["Starfsþörf"][("legudeild","Læknar")][0] = st.number_input("Fjöldi", value = STARFSDEMAND[("legudeild","Læknar")][0],max_value=40,step=1)
    simAttributes["Starfsþörf"][("legudeild","Hjúkrunarfræðingar")][0] = simAttributes["Starfsþörf"][("legudeild","Læknar")][0]
    simAttributes["Starfsþörf"][("legudeild","Læknar")][1] = SERF+SNL+SGL
    st.write("Veldu hversu marga sjúklinga á legudeild einn hjúkrunarfræðingur sér um.")
    numPatients = st.number_input("Fjöldi sjúklinga",value = 4,max_value=10,step = 1)
    simAttributes["Starfsþörf"][("legudeild","Hjúkrunarfræðingar")][1] = int(ceil(simAttributes["Starfsþörf"][("legudeild","Hjúkrunarfræðingar")][0]/numPatients))

st.divider()

st.header("Stillingar")
forstillt, stillingar = st.tabs(["Forstillt","Stillingar"])

with forstillt:
    scenarios = st.radio("Veldu forstillingu",("Default","Eldri þjóð","Yngri þjóð"))
    if scenarios == "Default":
        st.write("Þetta eru grunnstillingarnar sem byggðar eru á gögnum, þú getur séð þær í næsta flipa")
    if scenarios == "Eldri þjóð":
        st.write("Hversu mikið eldri er þjóðin?")
        t_G = st.slider("Prósentu aukning af eldra fólki", 0.0, 66.0, step = 1.0)
        t_M = st.slider("Prósentu aukning af miðaldra fólki", 0.0, 33.0, step = 1.0)
        t_U = -(t_G+t_M)
        t = [t_U,t_M,t_G]
    if scenarios == "Yngri þjóð":
        st.write("WIP")


#sliders o.fl.
with stillingar.expander("Hermunarstillingar"):
    if scenarios == "Default":
        simAttributes["meðalfjöldi"][AGE_GROUPS[0]] = st.number_input("Meðalfjöldi ungra á dag",min_value = 1, max_value=200,
                                                    value = copy(meanArrivaltimes[AGE_GROUPS[0]]),step = 1)
        simAttributes["meðalfjöldi"][AGE_GROUPS[1]] = st.number_input("Meðalfjöldi miðaldra á dag",min_value = 1, max_value=200,
                                                    value = copy(meanArrivaltimes[AGE_GROUPS[1]]),step = 1)
        simAttributes["meðalfjöldi"][AGE_GROUPS[2]] = st.number_input("Meðalfjöldi aldraðra á dag",min_value = 1, max_value=200,
                                                    value = copy(meanArrivaltimes[AGE_GROUPS[2]]),step = 1)
    simAttributes["Upphafslíkur"][0] = st.slider("Líkur á að nýr sjúklingur fari á legudeild", 
                                                    value = simAttributes["Upphafslíkur"][0])
    simAttributes["CAP"] = st.slider("Hámarskfjöldi á spítala",min_value = 50,max_value = 500,value = 50,step = 10)
    simAttributes["STOP"] = st.number_input("Fjöldi hermunardaga",min_value=10,max_value=1095,value=100)
    simAttributes["Fjöldi hermana"] = st.number_input("Fjöldi hermana",5,100,20)

if scenarios == "Eldri þjóð":
    tmp = copy(meanArrivaltimes)
    for i in range(len(AGE_GROUPS)):
        simAttributes["meðalfjöldi"][AGE_GROUPS[i]] = (1.0+t[i]/100.0)*tmp[AGE_GROUPS[i]]
# meðaltími milli koma á spítalann frá mismunandi aldurshópum. Hér höfum við default tímann.
keys = [age_group for age_group in AGE_GROUPS]
vals = [1.0/AGE_GROUP_AMOUNT[age_group] for age_group in AGE_GROUPS]

simAttributes["meðalbið"] = dict(zip(keys,vals))
simAttributes["Upphafslíkur"][1] = 1 - simAttributes["Upphafslíkur"][0]
simAttributes["lambda"] = sum([1.0/simAttributes["meðalbið"][age] for age in AGE_GROUPS])

st.divider()

st.header("Hermun")

st.text("Sjá eina hermun með völdum hermunarstillingum")
start = st.button("Start")

if start:
    data = sim(True,simAttributes)
    tot_leg_age = [sum(data[(aldur, "legudeild")]) for aldur in AGE_GROUPS]
    tot_leg = sum(tot_leg_age)
    tot_gong_age = [sum(data[(aldur, "göngudeild")]) for aldur in AGE_GROUPS]
    tot_gong = sum(tot_gong_age)
    st.write(f"Meðalfjöldi á legudeild er {tot_leg/simAttributes['STOP']} og meðalfjöldi á göngudeild er {tot_gong/simAttributes['STOP']}")
    st.write(f"meðal starsþörf miðað við enga bið:")
    d = [(key_soy[0],key_soy[1],val) for key_soy,val in data["Læknar"].items()]
    df = pd.DataFrame(d,columns = ["Deild","Starfsheiti","Fjöldi"])
    df = df.set_index(["Deild","Starfsheiti"])
    st.dataframe(df)

st.text("Hermunarstillingar")

KEYS_LEGU = [(AGE_GROUPS[0],STATES[0]),
            (AGE_GROUPS[1],STATES[0]),
            (AGE_GROUPS[2],STATES[0])]
KEYS_GONGU = [(AGE_GROUPS[0],STATES[1]),
            (AGE_GROUPS[1],STATES[1]),
            (AGE_GROUPS[2],STATES[1])]
KEYS_TOT = KEYS_GONGU + KEYS_LEGU

totalData = {
    "spitaliAmount" : [],
    "meðal lega" : [],
    "Sankey" : {},
    "dagar yfir cap" : [],
    "CI" : [],
    "heildarsjúklingar" : [],
    "Læknar" : {key : [] for key in simAttributes["Starfsþörf"]}
}
for key in KEYS_TOT:
    totalData[key] = []

hundur = st.button("Byrja hermun!")
if hundur:
    with st.spinner("Hermun í gangi..."):
        L = simAttributes["Fjöldi hermana"]
        totalData = hermHundur(totalData,simAttributes)
        legudataUngir = totalData[(simAttributes["Aldurshópar"][0],STATES[0])]
        legudataMid = totalData[(simAttributes["Aldurshópar"][1],STATES[0])]
        legudataGamlir = totalData[(simAttributes["Aldurshópar"][2],STATES[0])]
        df = pd.DataFrame(
            {
                "Legudeild ungir": legudataUngir,
                "Legudeild miðaldra": legudataMid,
                "Legudeild Gamlir" : legudataGamlir
            }
        )
        st.write("Hér er meðalfjöldi fólks á legudeild eftir aldursflokki.")
        fig1 = px.box(df,labels = {"variable" : "Aldursflokkur", "value" : "meðalfjöldi á legudeild"})
        st.plotly_chart(fig1)
        st.text(f"Hér sést meðalfjöldi einstaklinga í kerfinu á dag yfir þessar {L} hermanir ásamt 95% vikmörkum.")
        days = simAttributes["STOP"] -1
        mean_stay = totalData["meðal lega"]
        CI = totalData["CI"]
        lower,upper = [],[]
        for i in range(days):
            lower.append(CI[i][0])
            upper.append(CI[i][1])
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
                    y = upper + lower[::-1],
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
        sankeyData = totalData["Sankey"]
        nodeNum = {simAttributes["Stöður"][i] : i for i in range(len(simAttributes["Stöður"]))}
        source = []
        target = []
        for tvennd in simAttributes["deildaskipti"]:
            source.append(nodeNum[tvennd[0]])
            target.append(nodeNum[tvennd[1]])
        data_graph = [np.sum(sankeyData[key])/L for key in simAttributes["deildaskipti"]]
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
        meanWork = {}
        for keys in simAttributes["Starfsþörf"]:
            meanWork[keys] = sum(totalData["Læknar"][keys])/L
        d = [(key_soy[0],key_soy[1],val) for key_soy,val in meanWork.items()]
        df = pd.DataFrame(d,columns = ["Deild","Starfsheiti","Fjöldi"])
        df = df.set_index(["Deild","Starfsheiti"])
        st.write(f"meðal starsþörf miðað við enga bið:")
        st.dataframe(df)
        meanFjoldi_patient = sum(totalData["heildarsjúklingar"])/L
        st.write(f"Meðalfjöldi daga sem sjúklingar á spítala voru yfir hámark voru {meanYfirCap}. Meðalfjöldi einstakra sjúklinga sem komu", 
                 f"í kerfið voru {meanFjoldi_patient}")

    st.success("Hermun lokið")

prof = st.button("Skoða tíma profile")

if prof:
    pr = cProfile.Profile()
    pr.enable()
    res = hermHundur(totalData,simAttributes)
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr,stream = s).sort_stats("tottime")
    ps.print_stats()
    with open("time.txt","w+") as f:
        f.write(s.getvalue())

print(time()-start_time)