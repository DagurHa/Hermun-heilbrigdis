from itertools import product
from copy import copy
import pandas as pd

def data_use(data):
    dataOut = {
        "MeanLega" : [],
        "Sankey" : {},
        "totalPatient" : [],
        "BoxPlot": {},
        "StarfsInfo": {},
        "MeanAmount": {}
    }
    dataOut["MeanLega"] = data["MeanLega"]
    for keys in data["Sankey"]:
        keyTup = parse_tuple_string(keys)
        dataOut["Sankey"][keyTup] = data["Sankey"][keys]
    dataOut["totalPatient"] = data["totalPatient"]
    for keys in data["BoxPlot"]:
        keyTup = parse_tuple_string(keys)
        dataOut["BoxPlot"][keyTup] = data["BoxPlot"][keys]
    for keys in data["StarfsInfo"]:
        keyTup = parse_tuple_string(keys)
        dataOut["StarfsInfo"][keyTup] = data["StarfsInfo"][keys]
    for keys in data["MeanAmount"]:
        keyTup = parse_tuple_string(keys)
        dataOut["MeanAmount"][keyTup] = data["MeanAmount"][keys]
    dataAge = []
    dataStates = []
    for kvp in dataOut["MeanAmount"]:
        if not dataAge.__contains__(kvp[0]):
            dataAge.append(kvp[0])
        if not dataStates.__contains__(kvp[1]):
            dataStates.append(kvp[1])
    dataOut["AgeGroups"] = dataAge
    dataOut["States"] = dataStates
    return dataOut

def tup_to_string(dict):
    return {str(key):dict[key] for key in dict}

def parse_tuple_string(s):
    # Remove the outer parentheses from the string
    s = s.strip("()")

    # Split the string by comma and remove any leading/trailing whitespace
    items = [item.strip() for item in s.split(',')]

    # Convert the list of strings into a tuple
    result_tuple = tuple(items)

    return result_tuple

d_skra = pd.read_csv("dagar.csv")

#Hér eftir koma allar global breytur.
# Mismunandi stöður sjúklings. Bætum við og breytum þegar lengra er komið.
STATES = ["legudeild", "dagdeildarlota", "göngudeildarlota", "bráðamóttaka", "heilsugæsla", "hjúkrun", "dauði", "heim","einkageiri"]
LOTUDEILDIR = ["dagdeildarlota","göngudeildarlota"]
AGE_GROUPS = ["Ungur","Miðaldra","Gamall"] # mismunandi aldurshópar sjúklings. Breytum/bætum við mögulega
# meðalfjöldi aldurshópa sem koma á spítala á dag, fáum rauntölur hér og getum síðan breytt
AGE_GROUP_AMOUNT = {
    AGE_GROUPS[0] : 1331,
    AGE_GROUPS[1] : 389,
    AGE_GROUPS[2] : 328
}
# færslulíkur milli deilda, hér höfum við default færslulíkur sem verða vonandi byggðar á gögnum.
# Skiptum færslulíkum eftir aldri en bara til þess að aldrað fólk geti komist á hjúkrun, einmitt nuna er hjúkrun absorbing
#37% sem utskrifast af legudeild fara á göngudeild
PROB = {
    #Færslulíkur ungra
    (STATES[0],AGE_GROUPS[0]) : [0.0, 0.028, 0.199, 0.0, 0.0, 0.0, 0.04, 0.448, 0.285],
    (STATES[1],AGE_GROUPS[0]) : [0.211, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.789, 0.0], # Getum í c# um leið og einstaklingur fer inn ákveðið hvert hann fer eftir dagdeildarlotu, ef það er legudeild þá færa strax
    (STATES[2],AGE_GROUPS[0]) : [0.035, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.965, 0.0],
    (STATES[3],AGE_GROUPS[0]) : [0.126, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.874, 0.0],
    (STATES[4],AGE_GROUPS[0]) : [0.0, 0.00438, 0.0173, 0.0, 0.0, 0.0, 0.0, 0.88932, 0.089],
    (STATES[5],AGE_GROUPS[0]) : [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
    (STATES[6],AGE_GROUPS[0]) : [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
    (STATES[7],AGE_GROUPS[0]) : [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
    (STATES[8],AGE_GROUPS[0]) : [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
    #Færslulíkur miðaldra
    (STATES[0],AGE_GROUPS[1]) : [0.0, 0.033, 0.313, 0.0, 0.0, 0.0019, 0.04, 0.5087, 0.1034],
    (STATES[1],AGE_GROUPS[1]) : [0.174, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.826, 0.0], 
    (STATES[2],AGE_GROUPS[1]) : [0.03, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.97, 0.0],
    (STATES[3],AGE_GROUPS[1]) : [0.196, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.804, 0.0],
    (STATES[4],AGE_GROUPS[1]) : [0.0, 0.00794, 0.0138, 0.0, 0.0, 0.0, 0.0, 0.88926, 0.089],
    (STATES[5],AGE_GROUPS[1]) : [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
    (STATES[6],AGE_GROUPS[1]) : [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
    (STATES[7],AGE_GROUPS[1]) : [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
    (STATES[8],AGE_GROUPS[1]) : [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
    #Færslulíkur aldraðra (Hér breytast líkur á að fara til hjúkrunar, einmitt nuna ekki byggt á gögnum)
    (STATES[0],AGE_GROUPS[2]) : [0.0, 0.014, 0.178, 0.0, 0.0, 0.168, 0.04, 0.479, 0.121],
    (STATES[1],AGE_GROUPS[2]) : [0.234, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.766, 0.0], 
    (STATES[2],AGE_GROUPS[2]) : [0.043, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.957, 0.0],
    (STATES[3],AGE_GROUPS[2]) : [0.394, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.606, 0.0],
    (STATES[4],AGE_GROUPS[2]) : [0.0, 0.0083, 0.0134, 0.0, 0.0, 0.0, 0.0, 0.8893, 0.089],
    (STATES[5],AGE_GROUPS[2]) : [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
    (STATES[6],AGE_GROUPS[2]) : [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
    (STATES[7],AGE_GROUPS[2]) : [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
    (STATES[8],AGE_GROUPS[2]) : [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]
}
# Gott að hafa upphafsdeild : heilsugæsla og bráðamóttaka
# millideildir : legudeild og göngudeild
# endadeildir : hjúkrun, dauði og heim
UPPHAFSDEILD = [STATES[3],STATES[4]]
MILLIDEILD = LOTUDEILDIR + ["legudeild"]
print(MILLIDEILD)
ENDADEILD = [STATES[5],STATES[6],STATES[7],STATES[8]]
INITIAL_PROB = [0.12, 0.88] # Upphafslíkur á að fara á legudeild ,göngudeild og bráðamóttöku
# meðalbiðtímar á göngu- og legudeild, þetta verður default biðin sem byggist nú á aldri og verður vonandi byggð á gögnum.
#WAIT_BMT = {0.0,0.39}  Þarf að finna gögn um þetta (biðtími á bráðamóttöku)

#Notum bara hreinu meðaltölin sem fjölda daga í lotu
LOTUDAGAR = {
    (AGE_GROUPS[0], LOTUDEILDIR[0]) : 84.28,
    (AGE_GROUPS[0], LOTUDEILDIR[1]) : 87.0,
    (AGE_GROUPS[1], LOTUDEILDIR[0]) : 256.0,
    (AGE_GROUPS[1], LOTUDEILDIR[1]) : 79.0,
    (AGE_GROUPS[2], LOTUDEILDIR[0]) : 293.0,
    (AGE_GROUPS[2], LOTUDEILDIR[1]) : 89.0
}
LOTUKOMUR = {
    (AGE_GROUPS[0], LOTUDEILDIR[0]) : 2.72,
    (AGE_GROUPS[0], LOTUDEILDIR[1]) : 3.93,
    (AGE_GROUPS[1], LOTUDEILDIR[0]) : 4.10,
    (AGE_GROUPS[1], LOTUDEILDIR[1]) : 4.09,
    (AGE_GROUPS[2], LOTUDEILDIR[0]) : 4.28,
    (AGE_GROUPS[2], LOTUDEILDIR[1]) : 3.99
}
#Upphafslíkur á að fara í dagdeildar eða göngudeildar lotu
WAIT_LEGU = {
    AGE_GROUPS[0] : (0.9163, 0.8444),
    AGE_GROUPS[1] : (1.2385, 0.9410),
    AGE_GROUPS[2] : (1.5547, 0.97707)
}
WAIT_lognorm = {
    STATES[0] : WAIT_LEGU
}
L = 20
skiptiKeys = []
for tvennd in product(STATES,range(len(STATES))):
    if PROB[(tvennd[0],AGE_GROUPS[2])][tvennd[1]] > 0.0:
        skiptiKeys.append((tvennd[0],STATES[tvennd[1]]))
for deild in UPPHAFSDEILD:
    skiptiKeys.append(("hjúkrun",deild))
    skiptiKeys.append(("heim",deild))
deildaskipti = {keys : 0 for keys in skiptiKeys}
STORF = ["Læknar","Hjúkrunarfræðingar"]
# Fyrri talan í listanum segir til um hversu marga rýmir og seinni um hversu margir starfsmenn
STARFSDEMAND = {
    (STATES[0],STORF[0]) : [20,3],      #Miðum við að hver legudeild rúmi 20 sjúklinga og að hver legudeild hafi 3 lækna og 4 hjúkrunarfræðinga     #Miðum við að hver göngudeildarlæknir geti séð 12 sjúklinga á dag og þurfi einn hjúkrunarfræðing
    (STATES[0],STORF[1]) : [20,4],
    (STATES[4],STORF[0]): [10,1],
    (STATES[4],STORF[1]): [5,1],
    (STATES[3],STORF[0]): [10,1],
    (STATES[3],STORF[1]): [1,1]
}
KEYS_TOT = list(product(AGE_GROUPS,UPPHAFSDEILD+MILLIDEILD))

UPPHITUN = 30 # Upphitunartími hverrar hermunar, þ.e. byrjum ekki að safna/sýna upplýsingar fyrr en svona margir dagar hafa liðið
simAttributes_nontuple = {
    "MeanArrive" : AGE_GROUP_AMOUNT,
    "InitialProb" : INITIAL_PROB,
    "States" : STATES,
    "AgeGroups" : AGE_GROUPS,
    "WaitLognorm" : WAIT_lognorm,
    "SimAmount" : L,
    "PeriodStates" : LOTUDEILDIR,
    "InitState" : UPPHAFSDEILD,
    "MedState" : MILLIDEILD,
    "FinalState" : ENDADEILD,
    "WarmupTime" : UPPHITUN,
    "Keys" : KEYS_TOT,
    "Jobs" : STORF
}
simAttributes_tuple = {
    'MoveProb' : PROB,
    'Deildaskipti' : deildaskipti,
    'JobDemand' : STARFSDEMAND,
    "PeriodDays" : LOTUDAGAR,
    "PeriodStays" : LOTUKOMUR
}
GOGN = d_skra["Fjöldi koma á legudeild per dag"].tolist()
meanArrivaltimes = copy(simAttributes_nontuple["MeanArrive"])