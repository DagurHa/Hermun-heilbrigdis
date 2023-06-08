import random
import numpy as np
import plotly.graph_objects as go
"""
fig = go.Figure(go.Sankey(
    arrangement = "snap",
    node = {
        "label": ["Legudeild", "Göngudeild", "Dauði", "Heim", "Spítali"],
        'pad':10},  # 10 Pixels
    link = {
        "source": [0, 0, 0, 1, 1, 4],
        "target": [1, 2, 3, 3, 4, 1],
        "value": [0.3, 0.1, 0.6, 0.5, 0.5, 0.5]}))

fig.show()
"""
def flow(deildaskipti):
    trans = {}
    stays = {}
    for i in deildaskipti:
        state1,state2 = i
        if state1 != state2:
            if state1 not in trans:
                trans[state1] = {}
            if state2 not in trans[state1]:
                trans[state1][state2] = 0
            trans[state1][state2] += 1
        else:
            if state1 not in stays:
                stays[state1] = 0
            stays[state1] += 1
    
    dlisti = []
    countlisti = []
    # Transitions
    for state1, state2_counts in trans.items():
        for state2, count in state2_counts.items():
            print(f"Farið frá {state1} yfir til {state2}: {count}")
            dlisti.append((state1,state2))
            countlisti.append(count)
    # Stays
    staylisti = []
    count2listi = []
    for state,count in stays.items():
        print(f"Fóru aftur á {state}: {count}")
        staylisti.append((state,state))
        count2listi.append(count)
    countlisti.append(count2listi[0])
    dlisti.append(staylisti[0])
    info1 = dlisti
    info2 = countlisti
    return info1,info2