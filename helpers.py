from itertools import product

#Hér eftir koma allar global breytur.
# Mismunandi stöður sjúklings. Bætum við og breytum þegar lengra er komið.
STATES = ["legudeild", "göngudeild", "dauði", "heim"]
AGE_GROUPS = ["Ungur","Miðaldra","Gamall"] # mismunandi aldurshópar sjúklings. Breytum/bætum við mögulega
# meðalfjöldi aldurshópa sem koma á spítala á dag, fáum rauntölur hér og getum síðan breytt
AGE_GROUP_AMOUNT = {
    AGE_GROUPS[0] : 10,
    AGE_GROUPS[1] : 15,
    AGE_GROUPS[2] : 30
}
# færslulíkur milli deilda, hér höfum við default færslulíkur sem verða vonandi byggðar á gögnum. 
# Síðan er líka hægt að breyta í streamlit.
PROB = {
    STATES[0] : [0.0, 0.3, 0.1, 0.6],
    STATES[1] : [0.25, 0.0, 0.0, 0.75],
    STATES[2] : [0.0, 0.0, 1.0, 0.0],
    STATES[3] : [0.0, 0.0, 0.0, 1.0]
}
INITIAL_PROB = [0.3, 0.7] # Upphafslíkur á að fara á legudeild og göngudeild (þessu mun verða breytt)
# meðalbiðtímar á göngu- og legudeild, þetta verður default biðin sem byggist nú á aldri og verður vonandi byggð á gögnum.
#Pæling að hafa dag-/göngudeild alltaf einn dag og einhverjar líkur á að göngu-/dagdeildarsjúklingar fari á legudeild
MEAN_WAIT_TIMES = {
    (AGE_GROUPS[0], STATES[0]) : 2.0, (AGE_GROUPS[0], STATES[1]) : 0.01,
    (AGE_GROUPS[1], STATES[0]) : 3.0, (AGE_GROUPS[1], STATES[1]) : 0.02,
    (AGE_GROUPS[2], STATES[0]) : 5.0, (AGE_GROUPS[2], STATES[1]) : 0.04
}
L = 20
skiptiKeys = []
for tvennd in product(STATES,range(len(STATES))):
    if PROB[tvennd[0]][tvennd[1]] > 0.0:
        skiptiKeys.append((tvennd[0],STATES[tvennd[1]]))
deildaskipti = {keys : 0 for keys in skiptiKeys}
simAttributes = {
    "meðalfjöldi" : AGE_GROUP_AMOUNT,
    "Færslulíkur" : PROB,
    "Upphafslíkur" : INITIAL_PROB,
    "Stöður" : STATES,
    "Aldurshópar" : AGE_GROUPS,
    "Biðtímar" : MEAN_WAIT_TIMES,
    "Fjöldi hermana" : L,
    "deildaskipti" : deildaskipti
}