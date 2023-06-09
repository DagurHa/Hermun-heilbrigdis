import time
import streamlit as st
import time
from helpers import *
from simulation import sim,hermHundur

## Hér kemur streamlit kóðinn

#Athuga gæti verið gott að setja default sim attributes lika

start_time = time.time()
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
    L = st.number_input("Fjöldi hermana",5,100,20)

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
    (STATES[0],AGE_GROUPS[0]) : [],
    (STATES[0],AGE_GROUPS[1]) : [],
    (STATES[0],AGE_GROUPS[2]) : [],
    "spitaliAmount" : []
}

hundur = st.button("Byrja hermun!")
if hundur:
    with st.spinner("Hermun í gangi..."):
        hermHundur(hundur,totalData)
    st.success("Hermun lokið")
print(time.time()-start_time)
print(L)


