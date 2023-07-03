from itertools import product
from copy import copy
#from gogntilnotkunar import * 

#Hér eftir koma allar global breytur.
# Mismunandi stöður sjúklings. Bætum við og breytum þegar lengra er komið.
STATES = ["legudeild", "göngudeild", "dauði", "heim"]
AGE_GROUPS = ["Ungur","Miðaldra","Gamall"] # mismunandi aldurshópar sjúklings. Breytum/bætum við mögulega
# meðalfjöldi aldurshópa sem koma á spítala á dag, fáum rauntölur hér og getum síðan breytt
AGE_GROUP_AMOUNT = {
    AGE_GROUPS[0] : 54,
    AGE_GROUPS[1] : 41,
    AGE_GROUPS[2] : 36
}
# færslulíkur milli deilda, hér höfum við default færslulíkur sem verða vonandi byggðar á gögnum. 
#37% sem utskrifast af legudeild fara á göngudeild
PROB = {
    STATES[0] : [0.0, 0.31, 0.04, 0.65],
    STATES[1] : [0.05, 0.0, 0.0, 0.995],
    STATES[2] : [0.0, 0.0, 1.0, 0.0],
    STATES[3] : [0.0, 0.0, 0.0, 1.0]
}
UPPHAFSDEILD = [STATES[0],STATES[1]]
ENDADEILD = [STATES[2],STATES[3]]
INITIAL_PROB = [0.07, 0.93] # Upphafslíkur á að fara á legudeild og göngudeild (þessu mun verða breytt)
# meðalbiðtímar á göngu- og legudeild, þetta verður default biðin sem byggist nú á aldri og verður vonandi byggð á gögnum.
#Pæling að hafa dag-/göngudeild alltaf einn dag og einhverjar líkur á að göngu-/dagdeildarsjúklingar fari á legudeild
WAIT_GONGU = (0.01,0.03)
WAIT_LEGU = {
    AGE_GROUPS[0] : (0.9163,0.8444),
    AGE_GROUPS[1] : (1.2385,0.9410),
    AGE_GROUPS[2] : (1.5547,0.97707) 
}
WAIT_TIMES = {
    STATES[0] : WAIT_LEGU,
    STATES[1] : WAIT_GONGU
}
L = 20
skiptiKeys = []
for tvennd in product(STATES,range(len(STATES))):
    if PROB[tvennd[0]][tvennd[1]] > 0.0:
        skiptiKeys.append((tvennd[0],STATES[tvennd[1]]))
for deild in UPPHAFSDEILD:
    skiptiKeys.append(("heim",deild))
deildaskipti = {keys : 0 for keys in skiptiKeys}
ENDURKOMA = {
    AGE_GROUPS[0] : 0.02,
    AGE_GROUPS[1] : 0.04,
    AGE_GROUPS[2] : 0.06
}
STORF = ["Læknar","Hjúkrunarfræðingar"]
STARFSDEMAND = {
    (STATES[0],STORF[0]): [20,3],      #Miðum við að hver legudeild rúmi 20 sjúklinga og að hver legudeild hafi 3 lækna og 4 hjúkrunarfræðinga
    (STATES[1],STORF[0]) : [12,1],      #Miðum við að hver göngudeildarlæknir geti séð 12 sjúklinga á dag og þurfi einn hjúkrunarfræðing
    (STATES[0],STORF[1]) : [20,5],
    (STATES[1],STORF[1]) : [12,1]
}
KEYS_TOT = list(product(AGE_GROUPS,UPPHAFSDEILD))
UPPHITUN = 1 # Upphitunartími hverrar hermunar, þ.e. byrjum ekki að safna/sýna upplýsingar fyrr en svona margir dagar hafa liðið
simAttributes = {
    "meðalfjöldi" : AGE_GROUP_AMOUNT,
    "Færslulíkur" : PROB,
    "Upphafslíkur" : INITIAL_PROB,
    "Stöður" : STATES,
    "Aldurshópar" : AGE_GROUPS,
    "Biðtímar" : WAIT_TIMES,
    "Fjöldi hermana" : L,
    "deildaskipti" : deildaskipti,
    "Upphafsstöður" : UPPHAFSDEILD,
    "Endastöður" : ENDADEILD,
    "Upphitunartími" : UPPHITUN,
    "Endurkoma" : ENDURKOMA,
    "Starfsþörf" : STARFSDEMAND,
    "Lyklar" : KEYS_TOT,
    "Störf" : STORF
}
meanArrivaltimes = copy(simAttributes["meðalfjöldi"])