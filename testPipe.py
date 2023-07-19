from itertools import product
from copy import copy
#import pandas as pd
import json
import subprocess

#d_skra = pd.read_csv("dagar.csv")

#Kóði til að lesa dict úr csv
"""with open('dict.csv') as csv_file:
    reader = csv.reader(csv_file)
    mydict = dict(reader)"""

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
    str((STATES[0],AGE_GROUPS[0])) : [0.0, 0.31, 0.0, 0.0, 0.0, 0.04, 0.65],
    str((STATES[1],AGE_GROUPS[0])) : [0.005, 0.0, 0.0, 0.0, 0.0, 0.0, 0.995],
    str((STATES[2],AGE_GROUPS[0])) : [0.3, 0.3, 0.0, 0.0, 0.0, 0.0, 0.4],
    str((STATES[3],AGE_GROUPS[0])) : [0.03, 0.1, 0.005, 0.0, 0.0, 0.0, 0.865],
    str((STATES[4],AGE_GROUPS[0])) : [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
    str((STATES[5],AGE_GROUPS[0])) : [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
    str((STATES[6],AGE_GROUPS[0])) : [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
    #Færslulíkur miðaldra
    str((STATES[0],AGE_GROUPS[1])) : [0.0, 0.31, 0.0, 0.0, 0.0, 0.04, 0.65],
    str((STATES[1],AGE_GROUPS[1])) : [0.005, 0.0, 0.0, 0.0, 0.0, 0.0, 0.995],
    str((STATES[2],AGE_GROUPS[1])) : [0.3, 0.3, 0.0, 0.0, 0.0, 0.0, 0.4],
    str((STATES[3],AGE_GROUPS[1])) : [0.03, 0.1, 0.005, 0.0, 0.0, 0.0, 0.865],
    str((STATES[4],AGE_GROUPS[1])) : [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
    str((STATES[5],AGE_GROUPS[1])) : [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
    str((STATES[6],AGE_GROUPS[1])) : [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
    #Færslulíkur aldraðra (Hér breytast líkur á að fara til hjúkrunar, einmitt nuna ekki byggt á gögnum)
    str((STATES[0],AGE_GROUPS[2])) : [0.0, 0.31, 0.0, 0.0, 0.1, 0.04, 0.55],
    str((STATES[1],AGE_GROUPS[2])) : [0.005, 0.0, 0.0, 0.0, 0.1, 0.0, 0.895],
    str((STATES[2],AGE_GROUPS[2])) : [0.3, 0.3, 0.0, 0.0, 0.0, 0.0, 0.4],
    str((STATES[3],AGE_GROUPS[2])) : [0.03, 0.1, 0.005, 0.0, 0.0, 0.0, 0.865],
    str((STATES[4],AGE_GROUPS[2])) : [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
    str((STATES[5],AGE_GROUPS[2])) : [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
    str((STATES[6],AGE_GROUPS[2])) : [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
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
    if PROB[str((tvennd[0],AGE_GROUPS[2]))][tvennd[1]] > 0.0:
        skiptiKeys.append(str((tvennd[0],STATES[tvennd[1]])))
for deild in UPPHAFSDEILD:
    skiptiKeys.append(str(("hjúkrun",deild)))
    skiptiKeys.append(str(("heim",deild)))
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
    str((STATES[0],STORF[0])) : [20,3],      #Miðum við að hver legudeild rúmi 20 sjúklinga og að hver legudeild hafi 3 lækna og 4 hjúkrunarfræðinga
    str((STATES[1],STORF[0])) : [4,1],      #Miðum við að hver göngudeildarlæknir geti séð 12 sjúklinga á dag og þurfi einn hjúkrunarfræðing
    str((STATES[0],STORF[1])) : [20,4],
    str((STATES[1],STORF[1])) : [1,1],
    str((STATES[2],STORF[0])): [10,1],
    str((STATES[2],STORF[1])): [5,1],
    str((STATES[3],STORF[0])): [10,1],
    str((STATES[3],STORF[1])): [1,1]
}
#GOGN = d_skra["Fjöldi á dag"].tolist()
#print(len(GOGN))
KEYS_TOT = list(product(AGE_GROUPS,UPPHAFSDEILD+MILLIDEILD))
for i in range(len(KEYS_TOT)):
    KEYS_TOT[i] = str(KEYS_TOT[i])
UPPHITUN = 25 # Upphitunartími hverrar hermunar, þ.e. byrjum ekki að safna/sýna upplýsingar fyrr en svona margir dagar hafa liðið
simAttributes = {
    "MeanArrive" : AGE_GROUP_AMOUNT,
    "MoveProb" : PROB,
    "InitialProb" : INITIAL_PROB,
    "States" : STATES,
    "AgeGroups" : AGE_GROUPS,
    "WaitLognorm" : WAIT_lognorm,
    "WaitUniform" : WAIT_unif,
    "SimAmount" : L,
    "DeildaSkipti" : deildaskipti,
    "InitState" : UPPHAFSDEILD,
    "MedState" : MILLIDEILD,
    "FinalState" : ENDADEILD,
    "WarmupTime" : UPPHITUN,
    "ReEnter" : ENDURKOMA,
    "JobDemand" : STARFSDEMAND,
    "Keys" : KEYS_TOT,
    "Jobs" : STORF
}
simAttributes["MeanExp"] = {
    AGE_GROUPS[0] : 0.5,
    AGE_GROUPS[1] : 0.7,
    AGE_GROUPS[2] : 0.9
}
simAttributes["Lam"] = 25.0
simAttributes["ShowSim"] = False
simAttributes["Stop"] = 23

simPip = json.dumps(simAttributes, ensure_ascii=False)

process = subprocess.Popen(["./SimProj/bin/Debug/net7.0/SimProj.exe", simPip], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
stdout, stderr = process.communicate()

if stderr:
    print(f"Error: {stderr}")
else:
    output = stdout.strip()
    print(output)
    print(len(output))