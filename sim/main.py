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

def initSimAttribs(simAttribs,tab,num_in_key,name,compare):
    with tab:
        st.header("Deildir")
        deildir = st.expander("Starfsupplýsingar")
        gongu,legu = deildir.tabs(["Göngudeild","Legudeild"])
        with gongu:
            st.write("Veldu hversu marga sjúklinga hver göngudeildalæknir getur séð um á dag.")
            simAttribs["Starfsþörf"][("göngudeild","Læknar")][0] = st.number_input("Fjöldi sjúklinga fyrir göngudeildalækna",value = STARFSDEMAND[("göngudeild","Læknar")][0],max_value=40,step =1,key=num_in_key[name][0])
            st.write("Veldu hversu marga sjúklinga hver göngudeildar hjúkrunarfræðingur getur séð um á dag.")
            simAttribs["Starfsþörf"][("göngudeild","Hjúkrunarfræðingar")][0] = st.number_input("Fjöldi sjúklinga fyrir göngudeilda hjúkrunarfræðinga",value = STARFSDEMAND[("göngudeild","Hjúkrunarfræðingar")][0],max_value=40,step =1,key = num_in_key[name][1])

        with legu:
            st.write("Veldu fjölda lækna á legudeild,")
            SERF = st.number_input("Sérfræðingur", value = 1,key = num_in_key[name][2])
            SNL = st.number_input("Sérnámslæknir", value = 1,key=num_in_key[name][3])
            SGL = st.number_input("Deildarlæknir",value = 1,key=num_in_key[name][4])
            st.write("Veldu legurými á einni legudeild.")
            simAttribs["Starfsþörf"][("legudeild","Læknar")][0] = st.number_input("Fjöldi legurýma", value = STARFSDEMAND[("legudeild","Læknar")][0],max_value=40,step=1,key = num_in_key[name][5])
            simAttribs["Starfsþörf"][("legudeild","Hjúkrunarfræðingar")][0] = simAttribs["Starfsþörf"][("legudeild","Læknar")][0]
            simAttribs["Starfsþörf"][("legudeild","Læknar")][1] = SERF+SNL+SGL
            st.write("Veldu hversu marga sjúklinga á legudeild einn hjúkrunarfræðingur sér um.")
            numPatients = st.number_input("Fjöldi sjúklinga",value = 4,max_value=10,step = 1,key=num_in_key[name][6])
            simAttribs["Starfsþörf"][("legudeild","Hjúkrunarfræðingar")][1] = int(ceil(simAttribs["Starfsþörf"][("legudeild","Hjúkrunarfræðingar")][0]/numPatients))

        st.divider()

        st.header("Hermunar stillingar")
        forstillt, stillingar = st.tabs(["Forstillt","Stillingar"])

        with forstillt:
            scenarios = st.radio("Veldu forstillingu",("Default","Eldri þjóð","Yngri þjóð"),key=num_in_key[name][7])
            if scenarios == "Default":
                st.write("Þetta eru grunnstillingarnar sem byggðar eru á gögnum, þú getur séð þær í næsta flipa")
            if scenarios == "Eldri þjóð":
                st.write("Hversu mikið eldri er þjóðin?")
                t_G = st.slider("Prósentu aukning af eldra fólki", 0.0, 66.0, step = 1.0,key=num_in_key[name][8])
                t_M = st.slider("Prósentu aukning af miðaldra fólki", 0.0, 33.0, step = 1.0,key=num_in_key[name][9])
                t_U = -(t_G+t_M)
                t = [t_U,t_M,t_G]
            if scenarios == "Yngri þjóð":
                st.write("WIP")


        #sliders o.fl.
        with stillingar.expander("Hermunarstillingar"):
            if scenarios == "Default":
                simAttribs["meðalfjöldi"][AGE_GROUPS[0]] = st.number_input("Meðalfjöldi ungra á dag",min_value = 1, max_value=200,
                                                            value = copy(meanArrivaltimes[AGE_GROUPS[0]]),step = 1,key=num_in_key[name][10])
                simAttribs["meðalfjöldi"][AGE_GROUPS[1]] = st.number_input("Meðalfjöldi miðaldra á dag",min_value = 1, max_value=200,
                                                            value = copy(meanArrivaltimes[AGE_GROUPS[1]]),step = 1,key=num_in_key[name][11])
                simAttribs["meðalfjöldi"][AGE_GROUPS[2]] = st.number_input("Meðalfjöldi aldraðra á dag",min_value = 1, max_value=200,
                                                            value = copy(meanArrivaltimes[AGE_GROUPS[2]]),step = 1,key=num_in_key[name][12])
            simAttribs["Upphafslíkur"][0] = st.slider("Líkur á að nýr sjúklingur fari á legudeild", 
                                                            value = simAttribs["Upphafslíkur"][0],key=num_in_key[name][13])
            simAttribs["CAP"] = st.slider("Hámarskfjöldi á spítala",min_value = 50,max_value = 500,value = 50,step = 10,key=num_in_key[name][14])
            if not compare:
                simAttribs["STOP"] = st.number_input("Fjöldi hermunardaga",min_value=10,max_value=1095,value=100,key=num_in_key[name][15])
                simAttribs["Fjöldi hermana"] = st.number_input("Fjöldi hermana",5,100,20,key=num_in_key[name][16])

        if scenarios == "Eldri þjóð":
            tmp = copy(meanArrivaltimes)
            for i in range(len(AGE_GROUPS)):
                simAttribs["meðalfjöldi"][AGE_GROUPS[i]] = (1.0+t[i]/100.0)*tmp[AGE_GROUPS[i]]
        # meðaltími milli koma á spítalann frá mismunandi aldurshópum. Hér höfum við default tímann.
        keys = [age_group for age_group in AGE_GROUPS]
        vals = [1.0/simAttribs["meðalfjöldi"][age_group] for age_group in AGE_GROUPS]

        simAttribs["meðalbið"] = dict(zip(keys,vals))
        #Einmitt núna er upphafslíkur á að fara inná göngudeild beint alltaf 1/4 af upphafslíkum BMT
        simAttribs["Upphafslíkur"][1] = 1/4*(1 - simAttribs["Upphafslíkur"][0])
        simAttribs["Upphafslíkur"][2] = 3/4*(1 - simAttribs["Upphafslíkur"][0])
        print(simAttribs["Upphafslíkur"])
        simAttribs["lambda"] = sum([1.0/simAttribs["meðalbið"][age] for age in AGE_GROUPS])
    return simAttribs

## Hér kemur streamlit kóðinn

start_time = time()
st.title("Hermun heilbrigðiskerfisins")

compare = st.checkbox("Bera saman hermanir")

names = ["Hermun 1","Hermun 2"]
num_in_key = {
    "Hermun 1" : [i for i in range(25)],
    "Hermun 2" : [i for i in range(26,51)]
    }
if compare:
    simAttributes1 = deepcopy(simAttributes)
    simAttributes2 = deepcopy(simAttributes)
    simAttributes1["STOP"] = st.number_input("Fjöldi hermunardaga",min_value=10,max_value=1095,value=100)
    simAttributes1["Fjöldi hermana"] = st.number_input("Fjöldi hermana",5,100,20)
    simAttributes2["STOP"] = simAttributes1["STOP"]
    simAttributes2["Fjöldi hermana"] = simAttributes1["Fjöldi hermana"]
    hermun1,hermun2 = st.tabs(names)
    simAttributes1 = initSimAttribs(simAttributes1,hermun1,num_in_key,names[0],compare)
    simAttributes2 = initSimAttribs(simAttributes2,hermun2,num_in_key,names[1],compare)
    print(simAttributes1["lambda"])
    print(simAttributes2["lambda"])
else:
    hermun, reslts = st.tabs(["Hermun", "Niðurstöður"])
    simAttributes1 = deepcopy(simAttributes)
    simAttributes1 = initSimAttribs(simAttributes1,hermun,num_in_key,names[0],compare)
    with reslts:
        st.write("WIP")

#Velja fjölda hermunardaga úr gögn
data_graph = GOGN[400:399+simAttributes1["STOP"]]

st.divider()

st.header("Hermun")

st.text("Sjá eina hermun með völdum hermunarstillingum")
start = st.button("Start")

def calcSimShow(data):
    tot_leg_age = [sum(data[(aldur, "legudeild")]) for aldur in AGE_GROUPS]
    tot_leg = sum(tot_leg_age)
    tot_gong_age = [sum(data[(aldur, "göngudeild")]) for aldur in AGE_GROUPS]
    tot_gong = sum(tot_gong_age)
    tot_bmt_age = [sum(data[(aldur, "bráðamóttaka")]) for aldur in AGE_GROUPS]
    tot_bmt = sum(tot_bmt_age)
    d = [(key_soy[0],key_soy[1],val) for key_soy,val in data["Læknar"].items()]
    df = pd.DataFrame(d,columns = ["Deild","Starfsheiti","Fjöldi"])
    df_pivot = df.pivot(index="Deild",columns="Starfsheiti",values="Fjöldi")
    df_pivot.columns=["Læknar","Hjúkrunarfræðingar"]
    return [tot_leg,tot_gong,tot_bmt,df_pivot]

if start:
    data1 = sim(True,simAttributes1)
    [tot_leg,tot_gong,tot_bmt,df] = calcSimShow(data1)
    st.write(f"Meðalfjöldi á legudeild er {tot_leg/simAttributes1['STOP']} og meðalfjöldi á göngudeild er {tot_gong/simAttributes1['STOP']}")
    st.write(f"Meðalfjöldi á bráðamóttöku er {tot_bmt/simAttributes1['STOP']}") 
    st.write(f"og heildarfjöldi einstakra sjúklinga sem kom í kerfið var {data1['heildarsjúklingar']}")
    st.write(f"Meðal starfsþörf miðað við enga bið:")
    st.dataframe(df)
    if compare:
        st.write("Seinni hermun gefur.")
        data2 = sim(True,simAttributes2)
        [tot_leg,tot_gong,df] = calcSimShow(data2)
        st.write(f"Meðalfjöldi á legudeild er {tot_leg/simAttributes1['STOP']} og meðalfjöldi á göngudeild er {tot_gong/simAttributes1['STOP']}")
        st.write(f"Meðal starfsþörf miðað við enga bið:")
        st.dataframe(df)

st.text(f"Skoða niðurstöður úr {simAttributes1['Fjöldi hermana']} hermunum.")

KEYS_TOT = simAttributes1["Lyklar"]

def initTotalData():
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
    return totalData

def calcLegudata(totalData,simAttribs):
    legudataUngir = totalData[(simAttribs["Aldurshópar"][0],STATES[0])]
    legudataMid = totalData[(simAttribs["Aldurshópar"][1],STATES[0])]
    legudataGamlir = totalData[(simAttribs["Aldurshópar"][2],STATES[0])]
    return [legudataUngir,legudataMid,legudataGamlir]

def calcGraph(data,simAttribs,vis,first):
    days = simAttribs["STOP"] -1
    mean_stay = data["meðal lega"]
    CI = data["CI"]
    lower,upper = [],[]
    if first:
        c = "rgb(0,100,80)"
    else:
        c = "rgb(50,200,60)"
    for i in range(days):
        lower.append(CI[i][0])
        upper.append(CI[i][1])
    x = [i for i in range(days)]
    graf = [
            go.Scatter(
                x = x,
                y = mean_stay,
                line = dict(color = c),
                mode = "lines", 
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
    if first:
        graf[0].name = "Hermun 1"
        if vis:
            graf.append(go.Scatter(x = x,y = data_graph,name = "Raungögn"))
    else:
        graf[0].name = "Hermun 2"
    return graf

def calcSankey(data,simAttribs):
    L = simAttribs["Fjöldi hermana"]
    sankeyData = data["Sankey"]
    print(sankeyData)
    nodeNum = {simAttribs["Stöður"][i] : i for i in range(len(simAttribs["Stöður"]))}
    source = []
    target = []
    for tvennd in simAttribs["deildaskipti"]:
        source.append(nodeNum[tvennd[0]])
        target.append(nodeNum[tvennd[1]])
    data_graph = [np.sum(sankeyData[key])/L for key in simAttribs["deildaskipti"]]
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
    return fig3

def calcRandom(data,simAttribs):
    L = simAttribs["Fjöldi hermana"]
    meanYfirCap = np.sum(data["dagar yfir cap"])/L
    meanWork = {}
    for keys in simAttribs["Starfsþörf"]:
        meanWork[keys] = sum(data["Læknar"][keys])/L
    d = [(key_soy[0],key_soy[1],val) for key_soy,val in meanWork.items()]
    df = pd.DataFrame(d,columns=["Deild","Starfsheiti","Fjöldi"])
    df_pivot = df.pivot(index="Deild",columns="Starfsheiti",values="Fjöldi")
    df_pivot.columns=["Læknar","Hjúkrunarfræðingar"]
    meanFjoldi_patient = sum(totalData["heildarsjúklingar"])/L
    return [df_pivot,meanYfirCap,meanFjoldi_patient]

vis = st.checkbox("Sjá raungögn með hermun")
hundur = st.button("Byrja hermun!")
if hundur:
    with st.spinner("Hermun í gangi..."):
        totalData = initTotalData()
        totalData1 = hermHundur(totalData,simAttributes1)
        [legudataUngir,legudataMid,legudataGamlir] = calcLegudata(totalData1,simAttributes1)
        graf = calcGraph(totalData1,simAttributes1,vis,True)
        fig3 = calcSankey(totalData1,simAttributes1)
        df = pd.DataFrame(
            {
                "Legudeild Ungir": legudataUngir,
                "Legudeild Miðaldra": legudataMid,
                "Legudeild Gamlir" : legudataGamlir
            }
        )
        [df_starf,meanYfirCap,meanFjoldi_patient] = calcRandom(totalData1,simAttributes1)
        if compare:
            totalData = initTotalData()
            totalData2 = hermHundur(totalData,simAttributes2)
            [legudataUngir_new,legudataMid_new,legudataGamlir_new] = calcLegudata(totalData2,simAttributes1)
            graf_new = calcGraph(totalData2,simAttributes2,vis,False)
            fig3_new = calcSankey(totalData2,simAttributes2)
            df["Hermun"] = ["Hermun 1" for _ in range(simAttributes1["Fjöldi hermana"])]
            df_new = pd.DataFrame(
                {
                    "Legudeild Ungir" : legudataUngir_new,
                    "Legudeild Miðaldra" : legudataMid_new,
                    "Legudeild Gamlir" : legudataGamlir_new,
                    "Hermun" : ["Hermun 2" for _ in range(simAttributes2["Fjöldi hermana"])]
                },
                index = [simAttributes2["Fjöldi hermana"] + i for i in range(simAttributes2["Fjöldi hermana"])]
            )
            df_tot = pd.concat([df,df_new])
            graf_tot = graf + graf_new
            [df_starf_new,meanYfirCap_new,meanFjoldi_patient_new] = calcRandom(totalData2,simAttributes2)
        else:
            df_tot = df
            graf_tot = graf
    st.success("Hermun lokið")
    st.write("Hér er meðalfjöldi fólks á legudeild eftir aldursflokki.")
    if compare:
        fig1 = px.box(df_tot,color = "Hermun")
    else:
        fig1 = px.box(df_tot)
    st.plotly_chart(fig1)
    st.text(f"Hér sést meðalfjöldi einstaklinga í kerfinu á dag yfir þessar {L}")
    st.text(f"hermanir ásamt 95% vikmörkum.")
    fig2 = go.Figure(
        graf_tot
    )
    fig2.update_layout(
        xaxis_title = "Dagar",
        yaxis_title = "meðalfjöldi"
    )
    st.plotly_chart(fig2)
    fig3.update_layout(title_text="Flæði sjúklinga í gegnum kerfið")
    st.plotly_chart(fig3)
    if compare:
        fig3_new.update_layout(title_text="Flæði sjúklinga í gegnum kerfið í seinni hermun")
        st.plotly_chart(fig3_new)
    st.write(f"Meðal starfsþörf miðað við enga bið:")
    st.dataframe(df_starf)
    st.write(f"**Meðalfjöldi daga** þar sem fjöldi sjúklinga á spítala fóru yfir hámark voru **{meanYfirCap}**.")
    st.write(f"**Meðalfjöldi einstakra sjúklinga** sem komu í kerfið voru **{meanFjoldi_patient}**")
    if compare:
        st.write(f"Meðal starfsþörf miðað við enga bið í seinni hermun:")
        st.dataframe(df_starf_new)
        st.write(f"**Meðalfjöldi daga** þar sem fjöldi sjúklinga á spítala fóru yfir hámark voru **{meanYfirCap_new}**.")
        st.write(f"**Meðalfjöldi einstakra sjúklinga** sem komu í kerfið voru **{meanFjoldi_patient_new}**")


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
