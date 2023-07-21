from itertools import product
from copy import copy
#import pandas as pd
import json
import subprocess

#Hér eftir koma allar global breytur.
# Mismunandi stöður sjúklings. Bætum við og breytum þegar lengra er komið.
STATES = ["legudeild", "göngudeild", "bráðamóttaka", "heilsugæsla", "hjúkrun", "dauði", "heim"]
AGE_GROUPS = ["Ungur","Miðaldra","Gamall"] # mismunandi aldurshópar sjúklings. Breytum/bætum við mögulega
# meðalfjöldi aldurshópa sem koma á spítala á dag, fáum rauntölur hér og getum síðan breytt
AGE_GROUP_AMOUNT = {
    AGE_GROUPS[0] : 54,
    AGE_GROUPS[1] : 41,
    AGE_GROUPS[2] : 36
}
# færslulíkur milli deilda, hér höfum við default færslulíkur sem verða vonandi byggðar á gögnum.
# Skiptum færslulíkum eftir aldri en bara til þess að aldrað fólk geti komist á hjúkrun, einmitt nuna er hjúkrun absorbing
#37% sem utskrifast af legudeild fara á göngudeild
PROB = {
    #Færslulíkur ungra
    (STATES[0],AGE_GROUPS[0]) : [0.0, 0.31, 0.0, 0.0, 0.0, 0.04, 0.65],
    (STATES[1],AGE_GROUPS[0]) : [0.005, 0.0, 0.0, 0.0, 0.0, 0.0, 0.995],
    (STATES[2],AGE_GROUPS[0]) : [0.3, 0.3, 0.0, 0.0, 0.0, 0.0, 0.4],
    (STATES[3],AGE_GROUPS[0]) : [0.03, 0.1, 0.005, 0.0, 0.0, 0.0, 0.865],
    (STATES[4],AGE_GROUPS[0]) : [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
    (STATES[5],AGE_GROUPS[0]) : [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
    (STATES[6],AGE_GROUPS[0]) : [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
    #Færslulíkur miðaldra
    (STATES[0],AGE_GROUPS[1]) : [0.0, 0.31, 0.0, 0.0, 0.0, 0.04, 0.65],
    (STATES[1],AGE_GROUPS[1]) : [0.005, 0.0, 0.0, 0.0, 0.0, 0.0, 0.995],
    (STATES[2],AGE_GROUPS[1]) : [0.3, 0.3, 0.0, 0.0, 0.0, 0.0, 0.4],
    (STATES[3],AGE_GROUPS[1]) : [0.03, 0.1, 0.005, 0.0, 0.0, 0.0, 0.865],
    (STATES[4],AGE_GROUPS[1]) : [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
    (STATES[5],AGE_GROUPS[1]) : [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
    (STATES[6],AGE_GROUPS[1]) : [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
    #Færslulíkur aldraðra (Hér breytast líkur á að fara til hjúkrunar, einmitt nuna ekki byggt á gögnum)
    (STATES[0],AGE_GROUPS[2]) : [0.0, 0.31, 0.0, 0.0, 0.1, 0.04, 0.55],
    (STATES[1],AGE_GROUPS[2]) : [0.005, 0.0, 0.0, 0.0, 0.1, 0.0, 0.895],
    (STATES[2],AGE_GROUPS[2]) : [0.3, 0.3, 0.0, 0.0, 0.0, 0.0, 0.4],
    (STATES[3],AGE_GROUPS[2]) : [0.03, 0.1, 0.005, 0.0, 0.0, 0.0, 0.865],
    (STATES[4],AGE_GROUPS[2]) : [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
    (STATES[5],AGE_GROUPS[2]) : [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
    (STATES[6],AGE_GROUPS[2]) : [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]
}
# Gott að hafa upphafsdeild : heilsugæsla og bráðamóttaka
# millideildir : legudeild og göngudeild
# endadeildir : hjúkrun, dauði og heim
UPPHAFSDEILD = [STATES[2],STATES[3]]
MILLIDEILD = [STATES[0],STATES[1]]
ENDADEILD = [STATES[4],STATES[5],STATES[6]]
INITIAL_PROB = [0.75, 0.25] # Upphafslíkur á að fara á legudeild ,göngudeild og bráðamóttöku
# meðalbiðtímar á göngu- og legudeild, þetta verður default biðin sem byggist nú á aldri og verður vonandi byggð á gögnum.
WAIT_BMT = (0.0, 0.39) # Þarf að finna gögn um þetta (biðtími á bráðamóttöku)
WAIT_HH = (0.0, 0.2) # Þarf að finna gögn um þetta (Biðtími á heilsugæslu)
WAIT_GONGU = (0.01, 0.03)
WAIT_LEGU = {
    AGE_GROUPS[0] : (0.9163, 0.8444),
    AGE_GROUPS[1] : (1.2385, 0.9410),
    AGE_GROUPS[2] : (1.5547, 0.97707)
}
WAIT_unif = {
    STATES[1] : WAIT_GONGU,
    STATES[2] : WAIT_BMT,
    STATES[3] : WAIT_HH
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
#Erum ekki að nota þetta einmitt nuna, kannski seinna
ENDURKOMA = {
    AGE_GROUPS[0] : 0.02,
    AGE_GROUPS[1] : 0.04,
    AGE_GROUPS[2] : 0.06
}
STORF = ["Læknar","Hjúkrunarfræðingar"]
# Fyrri talan í listanum segir til um hversu marga rýmir og seinni um hversu margir starfsmenn
STARFSDEMAND = {
    (STATES[0],STORF[0]) : (20,3),      #Miðum við að hver legudeild rúmi 20 sjúklinga og að hver legudeild hafi 3 lækna og 4 hjúkrunarfræðinga
    (STATES[1],STORF[0]) : (4,1),      #Miðum við að hver göngudeildarlæknir geti séð 12 sjúklinga á dag og þurfi einn hjúkrunarfræðing
    (STATES[0],STORF[1]) : (20,4),
    (STATES[1],STORF[1]) : (1,1),
    (STATES[2],STORF[0]): (10,1),
    (STATES[2],STORF[1]): (5,1),
    (STATES[3],STORF[0]): (10,1),
    (STATES[3],STORF[1]): (1,1)
}
#GOGN = d_skra["Fjöldi á dag"].tolist()
#print(len(GOGN))
KEYS_TOT = list(product(AGE_GROUPS,UPPHAFSDEILD+MILLIDEILD))

UPPHITUN = 25 # Upphitunartími hverrar hermunar, þ.e. byrjum ekki að safna/sýna upplýsingar fyrr en svona margir dagar hafa liðið
simAttributes_nontuple = {
    "MeanArrive" : AGE_GROUP_AMOUNT,
    #"MoveProb" : PROB,
    "InitialProb" : INITIAL_PROB,
    "States" : STATES,
    "AgeGroups" : AGE_GROUPS,
    "WaitLognorm" : WAIT_lognorm,
    "WaitUniform" : WAIT_unif,
    "SimAmount" : L,
    #"DeildaSkipti" : deildaskipti,
    "InitState" : UPPHAFSDEILD,
    "MedState" : MILLIDEILD,
    "FinalState" : ENDADEILD,
    "WarmupTime" : UPPHITUN,
    "ReEnter" : ENDURKOMA,
    #"JobDemand" : STARFSDEMAND,
    "Keys" : KEYS_TOT,
    "Jobs" : STORF
}
simAttributes_tuple = {
    'MoveProb' : PROB,
    'Deildaskipti' : deildaskipti,
    'JobDemand' : STARFSDEMAND
}
simAttributes_nontuple["MeanExp"] = {
    AGE_GROUPS[0] : 0.5,
    AGE_GROUPS[1] : 0.7,
    AGE_GROUPS[2] : 0.9
}
simAttributes_nontuple["Lam"] = 25.0
simAttributes_nontuple["ShowSim"] = False
simAttributes_nontuple["Stop"] = 23

def tup_to_string(dict):
    return {str(key):dict[key] for key in dict}

simAttrib_tuple = {}
for key in simAttributes_tuple:
    simAttrib_tuple[key] = tup_to_string(simAttributes_tuple[key])

simPip_nontuple = json.dumps(simAttributes_nontuple,ensure_ascii=True)
simPip_tuple = json.dumps(simAttrib_tuple,ensure_ascii=True)

process = subprocess.Popen(["./SimProj/bin/Debug/net7.0/SimProj.exe", simPip_nontuple,simPip_tuple], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
stdout, stderr = process.communicate()

if stderr:
    print(f"Error: {stderr}")
else:
    output = stdout.strip()
    print(output)
    print(len(output))