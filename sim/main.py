from time import time
import streamlit as st
from helpers import *
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from copy import copy,deepcopy
from math import ceil
import json
from scipy import stats
import subprocess

def initSimAttribs(simAttribs_tuple,simAttribs_nontuple,tab,num_in_key,name,compare):
    with tab:
        st.header("Deildir")
        st.write("Hér getur þú valið hversu marga sjúklinga annað hvort læknir eða hjúkrúnarfræðingur"
                "getur séð um í einu á hverri deild. Þetta er þá miðað við að hver sjúklingur þarf ekki að bíða eftir aðstoð.")
        deildir = st.expander("Starfsupplýsingar")
        legu,bmt,hh = deildir.tabs(["Legudeild","Bráðamóttaka", "Heilsugæsla"])

        with legu:
            st.write("Veldu fjölda lækna á legudeild,")
            SERF = st.number_input("Sérfræðingur", value = 1,key = num_in_key[name][2])
            SNL = st.number_input("Sérnámslæknir", value = 1,key=num_in_key[name][3])
            SGL = st.number_input("Deildarlæknir",value = 1,key=num_in_key[name][4])
            st.write("Veldu legurými á einni legudeild.")
            simAttribs_tuple["JobDemand"][("legudeild","Læknar")][0] = st.number_input("Fjöldi legurýma", value = STARFSDEMAND[("legudeild","Læknar")][0],max_value=40,step=1,key = num_in_key[name][5])
            simAttribs_tuple["JobDemand"][("legudeild","Hjúkrunarfræðingar")][0] = simAttribs_tuple["JobDemand"][("legudeild","Læknar")][0]
            simAttribs_tuple["JobDemand"][("legudeild","Læknar")][1] = SERF+SNL+SGL
            st.write("Veldu hversu marga sjúklinga á legudeild einn hjúkrunarfræðingur sér um.")
            numPatients = st.number_input("Fjöldi sjúklinga",value = 4,max_value=10,step = 1,key=num_in_key[name][6])
            simAttribs_tuple["JobDemand"][("legudeild","Hjúkrunarfræðingar")][1] = int(ceil(simAttribs_tuple["JobDemand"][("legudeild","Hjúkrunarfræðingar")][0]/numPatients))

        with bmt:
            st.write("Veldu hversu marga sjúklinga hver bráðamóttökulæknir getur séð um í einu.")
            simAttribs_tuple["JobDemand"][("bráðamóttaka","Læknar")][0] = st.number_input("Fjöldi sjúklinga fyrir bráðamóttökulækna",value = STARFSDEMAND[("bráðamóttaka","Læknar")][0],max_value=40,step =1,key=num_in_key[name][19])
            st.write("Veldu hversu marga sjúklinga hver bráðamóttöku hjúkrunarfræðingur getur séð um í einu.")
            simAttribs_tuple["JobDemand"][("bráðamóttaka","Hjúkrunarfræðingar")][0] = st.number_input("Fjöldi sjúklinga fyrir bráðamóttöku hjúkrunarfræðinga",value = STARFSDEMAND[("bráðamóttaka","Hjúkrunarfræðingar")][0],max_value=40,step =1,key = num_in_key[name][20])

        with hh:
            st.write("Veldu hversu marga sjúklinga hver heilsugæslulæknir getur séð um í einu.")
            simAttribs_tuple["JobDemand"][("heilsugæsla","Læknar")][0] = st.number_input("Fjöldi sjúklinga fyrir heilsugæslulækna",value = STARFSDEMAND[("heilsugæsla","Læknar")][0],max_value=40,step =1,key=num_in_key[name][21])
            st.write("Veldu hversu marga sjúklinga hver heilsugæslu hjúkrunarfræðingur getur séð um í einu.")
            simAttribs_tuple["JobDemand"][("heilsugæsla","Hjúkrunarfræðingar")][0] = st.number_input("Fjöldi sjúklinga fyrir heilsugæslu hjúkrunarfræðinga",value = STARFSDEMAND[("heilsugæsla","Hjúkrunarfræðingar")][0],max_value=40,step =1,key = num_in_key[name][22])
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
        with stillingar:
            if scenarios == "Default":
                st.write("Veldu meðalfjölda sem koma á heilsugæslur og bráðamóttökur á dag.")
                simAttribs_nontuple["MeanArrive"][AGE_GROUPS[0]] = st.number_input("Meðalfjöldi ungra á dag",min_value = 1, max_value=3000,
                                                            value = copy(meanArrivaltimes[AGE_GROUPS[0]]),step = 1,key=num_in_key[name][10])
                simAttribs_nontuple["MeanArrive"][AGE_GROUPS[1]] = st.number_input("Meðalfjöldi miðaldra á dag",min_value = 1, max_value=3000,
                                                            value = copy(meanArrivaltimes[AGE_GROUPS[1]]),step = 1,key=num_in_key[name][11])
                simAttribs_nontuple["MeanArrive"][AGE_GROUPS[2]] = st.number_input("Meðalfjöldi aldraðra á dag",min_value = 1, max_value=3000,
                                                            value = copy(meanArrivaltimes[AGE_GROUPS[2]]),step = 1,key=num_in_key[name][12])
            simAttribs_nontuple["InitialProb"][0] = st.slider("Líkur á að nýr sjúklingur fari á bráðamóttöku", 
                                                            value = simAttribs_nontuple["InitialProb"][0],key=num_in_key[name][13])
            if not compare:
                simAttribs_nontuple["Stop"] = st.number_input("Fjöldi hermunardaga",min_value=10,max_value=1095,value=100,key=num_in_key[name][15])
                simAttribs_nontuple["SimAmount"] = st.number_input("Fjöldi hermana",5,100,20,key=num_in_key[name][16])

        if scenarios == "Eldri þjóð":
            tmp = copy(meanArrivaltimes)
            for i in range(len(AGE_GROUPS)):
                simAttribs_nontuple["MeanArrive"][AGE_GROUPS[i]] = (1.0+t[i]/100.0)*tmp[AGE_GROUPS[i]]
        # meðaltími milli koma á spítalann frá mismunandi aldurshópum. Hér höfum við default tímann.
        keys = [age_group for age_group in AGE_GROUPS]
        vals = [1.0/simAttribs_nontuple["MeanArrive"][age_group] for age_group in AGE_GROUPS]

        simAttribs_nontuple["MeanWait"] = dict(zip(keys,vals))
        #Einmitt núna er upphafslíkur á að fara inná göngudeild beint alltaf 1/4 af upphafslíkum BMT
        simAttribs_nontuple["InitialProb"][1] = 1 - simAttribs_nontuple["InitialProb"][0]
        simAttribs_nontuple["Lam"] = sum([1.0/simAttribs_nontuple["MeanWait"][age] for age in AGE_GROUPS])
    return [simAttribs_nontuple,simAttribs_tuple]

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
    simAttributes1_nontuple = deepcopy(simAttributes_nontuple)
    simAttributes1_tuple = deepcopy(simAttributes_tuple)
    simAttributes2_nontuple = deepcopy(simAttributes_nontuple)
    simAttributes2_tuple = deepcopy(simAttributes_tuple)
    simAttributes1_nontuple["Stop"] = st.number_input("Fjöldi hermunardaga",min_value=10,max_value=1095,value=100)
    simAttributes1_nontuple["SimAmount"] = st.number_input("Fjöldi hermana",5,100,20)
    simAttributes2_nontuple["Stop"] = simAttributes1_nontuple["Stop"]
    simAttributes2_nontuple["SimAmount"] = simAttributes1_nontuple["SimAmount"]
    hermun1,hermun2 = st.tabs(names)
    [simAttributes1_nontuple,simAttributes1_tuple] = initSimAttribs(simAttributes1_tuple,simAttributes1_nontuple,hermun1,num_in_key,names[0],compare)
    [simAttributes2_nontuple,simAttributes2_tuple] = initSimAttribs(simAttributes2_tuple,simAttributes2_nontuple,hermun2,num_in_key,names[1],compare)
else:
    hermun, reslts = st.tabs(["Hermun", "Niðurstöður"])
    simAttributes1_nontuple = deepcopy(simAttributes_nontuple)
    simAttributes1_tuple = deepcopy(simAttributes_tuple)
    [simAttributes1_nontuple,simAttributes1_tuple] = initSimAttribs(simAttributes1_tuple,simAttributes1_nontuple,hermun,num_in_key,names[0],compare)
    with reslts:
        st.write("WIP")

#Velja fjölda hermunardaga úr gögn
data_graph = GOGN[400:399+simAttributes1_nontuple["Stop"]]

st.divider()

st.header("Hermun")

st.text(f"Skoða niðurstöður úr {simAttributes1_nontuple['SimAmount']} hermunum.")

KEYS_TOT = simAttributes1_nontuple["Keys"]

def calcConfidence(data,stop,simAmount):
    dataIM = [[] for _ in range(simAmount)]
    total = [0 for _ in range(stop)]
    for i in range(simAmount):
        for j in range(stop):
            s = sum([data["MeanAmount"][(age_grp,"legudeild")][i][j] for age_grp in data["AgeGroups"]])
            total[j] += s
            dataIM[i].append(s)
    totalMean = [total[k]/simAmount for k in range(stop)]
    stayData_arr = np.array(dataIM)
    stayData_arr = np.transpose(stayData_arr)
    data["MeanLegaPerHerm"] = totalMean
    inter = []
    if L < 30:
        for i in range(stop):
            inter.append(stats.t.interval(confidence=0.95,df = len(stayData_arr[i,:])-1, loc = totalMean[i],
                                          scale = stats.sem(stayData_arr[i,:])))
    else:
        for i in range(stop):
            inter.append(stats.norm.interval(confidence=0.95,loc = totalMean[i],scale = stats.sem(stayData_arr[i,:])))
    return inter

def calcLegudata(data):
    legudataUngir = data["BoxPlot"][(data["AgeGroups"][0],"legudeild")]
    legudataMid = data["BoxPlot"][(data["AgeGroups"][1],"legudeild")]
    legudataGamlir = data["BoxPlot"][(data["AgeGroups"][2],"legudeild")]
    return [legudataUngir,legudataMid,legudataGamlir]

def calcGraph(data,days,vis,first):
    mean_stay = data["MeanLegaPerHerm"]
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

def calcSankey(data,simAttribs_nontuple,simAttribs_tuple):
    L = simAttribs_nontuple["SimAmount"]
    sankeyData = data["Sankey"]
    nodeNum = {simAttribs_nontuple["States"][i] : i for i in range(len(simAttribs_nontuple["States"]))}
    source = []
    target = []
    for tvennd in simAttribs_tuple["Deildaskipti"]:
        source.append(nodeNum[tvennd[0]])
        target.append(nodeNum[tvennd[1]])
    data_graph = [np.sum(sankeyData[key])/L for key in sankeyData]
    fig3 = go.Figure(go.Sankey(
    arrangement = "freeform",
    node = {
        "label": simAttribs_nontuple["States"],
        'pad':10},
    link = {
        "arrowlen" : 10,
        "source" : source,
        "target" : target,
        "value" : data_graph}))
    return fig3

def calcRandom(data,simAmount):
    meanWork = {}
    for keys in data["StarfsInfo"]:
        meanWork[keys] = sum(data["StarfsInfo"][keys])/simAmount
    d = [(key_soy[0],key_soy[1],val) for key_soy,val in meanWork.items()]
    df = pd.DataFrame(d,columns=["Deild","Starfsheiti","Fjöldi"])
    df_pivot = df.pivot(index="Deild",columns="Starfsheiti",values="Fjöldi")
    df_pivot.columns=["Hjúkrunarfræðingar","Læknar"]
    meanFjoldi_patient = sum(data["totalPatient"])/simAmount
    MeanTimeMean = {key_data : 0 for key_data in data["MeanTimeDeild"][0]}
    for dictItem in data["MeanTimeDeild"]:
        for key in dictItem:
            if dictItem[key] != "NaN":
                MeanTimeMean[key] += dictItem[key]
    for key in MeanTimeMean:
        MeanTimeMean[key] = MeanTimeMean[key]/simAmount
    return [df_pivot,meanFjoldi_patient,MeanTimeMean]

vis = st.checkbox("Sjá raungögn með hermun")
hundur = st.button("Byrja hermun!")
if hundur:
    with st.spinner("Hermun í gangi..."):
        simAttrib_tuple = {}
        for key in simAttributes1_tuple:
            simAttrib_tuple[key] = tup_to_string(simAttributes1_tuple[key])
            if key == "JobDemand":
                for keys in simAttributes1_tuple[key]:
                    simAttributes1_tuple[key][keys] = tuple(simAttributes1_tuple[key][keys])

        pth = "./sim/"
        file_nonTuple = pth + "InputNonTuple.json"
        file_tuple = pth + "InputTuple.json"
        with open(file_nonTuple,"w",encoding='utf8') as json_file:
            json.dump(simAttributes1_nontuple,json_file,ensure_ascii=False)
        with open(file_tuple,"w",encoding='utf8') as json_file:
            json.dump(simAttrib_tuple,json_file,ensure_ascii=False)
        
        subprocess.run(["dotnet",pth + "SimProj.dll"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,check=True)

        with open(pth+'JSONOUTPUT.json', 'r', encoding='utf-8-sig') as json_f:
            data = json.load(json_f)
        dataUse = data_use(data)
        dataUse["CI"] = calcConfidence(dataUse,simAttributes1_nontuple["Stop"],simAttributes1_nontuple["SimAmount"])
        [legudataUngir,legudataMid,legudataGamlir] = calcLegudata(dataUse)
        graf = calcGraph(dataUse,simAttributes1_nontuple["Stop"],vis,True)
        fig3 = calcSankey(dataUse,simAttributes1_nontuple,simAttributes1_tuple)
        df = pd.DataFrame(
            {
                "Legudeild Ungir": legudataUngir,
                "Legudeild Miðaldra": legudataMid,
                "Legudeild Gamlir" : legudataGamlir
            }
        )
        [df_starf,meanFjoldi_patient,MeanTimeDict] = calcRandom(dataUse,simAttributes1_nontuple["SimAmount"])
        data = {"Deild": [], "Aldur": [], "Meðal tími": []}
        for (group,unit), mean_wait in MeanTimeDict.items():
            data["Deild"].append(unit)
            data["Aldur"].append(group)
            data["Meðal tími"].append(mean_wait)
        MeanTimeDict_DF = pd.DataFrame(data)
        pivot_DF = MeanTimeDict_DF.pivot_table(index = "Deild", columns="Aldur", values="Meðal tími",aggfunc= "first")
        if compare:
            simAttrib_tuple = {}
            for key in simAttributes2_tuple:
                simAttrib_tuple[key] = tup_to_string(simAttributes2_tuple[key])
                if key == "JobDemand":
                    for keys in simAttributes2_tuple[key]:
                        simAttributes2_tuple[key][keys] = tuple(simAttributes2_tuple[key][keys])

            file_nonTuple = pth + "InputNonTuple.json"
            file_tuple = pth + "InputTuple.json"
            with open(file_nonTuple,"w") as json_file:
                json.dump(simAttributes2_nontuple,json_file,ensure_ascii=True)
            with open(file_tuple,"w") as json_file:
                json.dump(simAttrib_tuple,json_file,ensure_ascii=True)
        
            process = subprocess.Popen([pth+"SimProj.exe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()

            if stderr:
                print(f"Error: {stderr}")
        
            with open(pth+'JSONOUTPUT.json','r',encoding='utf-8-sig') as json_f2:
                data2 = json.load(json_f2)
            dataUse = data_use(data2)
            dataUse["CI"] = calcConfidence(dataUse,simAttributes2_nontuple["Stop"],simAttributes2_nontuple["SimAmount"])
            [legudataUngir_new,legudataMid_new,legudataGamlir_new] = calcLegudata(dataUse)
            graf_new = calcGraph(dataUse,simAttributes2_nontuple["Stop"],vis,False)
            fig3_new = calcSankey(dataUse,simAttributes2_nontuple,simAttributes2_tuple)
            df["Hermun"] = ["Hermun 1" for _ in range(simAttributes1_nontuple["SimAmount"])]
            df_new = pd.DataFrame(
                {
                    "Legudeild Ungir" : legudataUngir_new,
                    "Legudeild Miðaldra" : legudataMid_new,
                    "Legudeild Gamlir" : legudataGamlir_new,
                    "Hermun" : ["Hermun 2" for _ in range(simAttributes2_nontuple["SimAmount"])]
                },
                index = [simAttributes2_nontuple["SimAmount"] + i for i in range(simAttributes2_nontuple["SimAmount"])]
            )
            df_tot = pd.concat([df,df_new])
            graf_tot = graf + graf_new
            [df_starf_new,meanFjoldi_patient_new,MeanTimeDict_new] = calcRandom(dataUse,simAttributes2_nontuple["SimAmount"])
            data_new = {"Deild": [], "Aldur": [], "Meðal tími": []}
            for (group,unit), mean_wait in MeanTimeDict_new.items():
                data_new["Deild"].append(unit)
                data_new["Aldur"].append(group)
                data_new["Meðal tími"].append(mean_wait)
            MeanTimeDict_DF_new = pd.DataFrame(data_new)
            pivot_DF_new = MeanTimeDict_DF_new.pivot_table(index = "Deild", columns="Aldur", values="Meðal tími",aggfunc= "first")
        else:
            df_tot = df
            graf_tot = graf
    st.success("Hermun lokið")
    #st.write("Hér er fjöldi fólks á legudeild í lok dags eftir aldursflokki.")
    if compare:
        fig1 = px.box(df_tot,color = "Hermun")
        fig1.update_layout(title="Fjöldi fólks á legudeild í lok dags eftir aldursflokki")
        fig1.update_xaxes(title_text="Aldurshópar")
        fig1.update_yaxes(title_text="Dreifing á fjölda fólks")
    else:
        fig1 = px.box(df_tot)
        fig1.update_layout(title="Fjöldi fólks á legudeild í lok dags eftir aldurshópi")
        fig1.update_xaxes(title_text="Aldurshópar")
        fig1.update_yaxes(title_text="Dreifing á fjölda fólks")
    st.plotly_chart(fig1)
    st.text(f"Hér sést fjöldi einstaklinga sem koma á legudeild á dag yfir þessar {L}")
    st.text(f"hermanir ásamt 95% vikmörkum.")
    fig2 = go.Figure(
        graf_tot
    )
    fig2.update_layout(
        xaxis_title = "Dagar",
        yaxis_title = "Meðalfjöldi",
        title="Meðalfjöldi sjúklinga sem leggjast inn á legudeild á dag"
    )
    fig2.update_yaxes(rangemode="tozero")
    st.plotly_chart(fig2)
    fig3.update_layout(title_text="Flæði sjúklinga í gegnum kerfið")
    st.plotly_chart(fig3)
    if compare:
        fig3_new.update_layout(title_text="Flæði sjúklinga í gegnum kerfið í seinni hermun")
        st.plotly_chart(fig3_new)
    st.write("Meðaltími sjúklinga í kerfinu í hermun 1:")
    st.dataframe(pivot_DF)
    if compare:
        st.write("Meðaltími sjúklinga í kerfinu í hermun 2:")
        st.dataframe(pivot_DF_new)
    st.write(f"Meðal starfsþörf miðað við enga bið:")
    st.dataframe(df_starf)
    st.write(f"**Meðalfjöldi einstakra sjúklinga** sem komu í kerfið voru **{meanFjoldi_patient}**")
    if compare:
        st.write(f"Meðal starfsþörf miðað við enga bið í seinni hermun:")
        st.dataframe(df_starf_new)
        st.write(f"**Meðalfjöldi einstakra sjúklinga** sem komu í kerfið voru **{meanFjoldi_patient_new}**")
