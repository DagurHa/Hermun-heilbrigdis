import numpy as np
from random import expovariate, random,choice
from time import sleep
from pandas import DataFrame
from streamlit import line_chart
from simpy import Environment,Interrupt
#Ath þarf scipy version 1.10.1
from scipy import stats
from math import ceil

class Patient:
    def __init__(self,aldur,env,deild,numer):
        self.aldur = aldur
        self.env = env
        self.deild = deild
        self.timiSpitala = 0 # Þetta gæti verið gott í framtíð
        self.numer = numer # breyta fyrir aflúsun
    # Þegar sjúklingur er búinn á sinni deild finnum við hvert hann fer næst og sendum hann þangað
    def updatePatient(self,S):
        prev = self.deild
        i_deild = randomChoice(S.fastar["Færslulíkur"][(prev,self.aldur)])
        self.deild = S.fastar["Stöður"][i_deild]
        if S.upphitunFlag:
            S.fjoldi["deildaskipti"][(prev,self.deild)] += 1
        if self.deild == S.fastar["Stöður"][2] or self.deild == S.fastar["Stöður"][3]:
            S.removeP(prev,self)
        else:
            S.fjoldi[(self.aldur,prev)] -= 1
            yield self.env.process(S.addP(self,True,False))

class Spitali:
    def __init__(self,fjoldi,env,simAttributes):
        self.fjoldi = fjoldi
        self.env = env
        self.fastar = simAttributes
        self.cap = self.fastar["CAP"]
        self.p_age = [(1.0/self.fastar["meðalbið"][age])/self.fastar["lambda"] for age in self.fastar["Aldurshópar"]]
        self.telja = 0
        self.amount = 0 #sum(list(fjoldi.values()))
        self.discharged = {}
        self.endurkomur = 0
        self.action = env.process(self.patientGen(env))
        self.upphitun = env.event()
        env.process(self.upphitunWait())
        self.upphitunFlag = False
        self.homePatientWait = False
    def patientGen(self,env):
        while True:
            try:
                if len(self.discharged) > 0 and not self.homePatientWait:
                    env.process(self.homeGen(env,self.discharged))
                wait = expovariate(self.fastar["lambda"])
                #print(f"Þurfum að bíða í {wait} langann tíma eftir næsta sjúkling, liðinn tími er {env.now}")
                yield env.timeout(wait)
                i_aldur = randomChoice(self.p_age)
                aldur = self.fastar["Aldurshópar"][i_aldur]
                i_deild_upphaf = randomChoice(self.fastar["Upphafslíkur"])
                deild_upphaf = self.fastar["Upphafsstöður"][i_deild_upphaf]
                p = Patient(aldur,env,deild_upphaf,self.telja)
                #print(f"Sjúklingur númer {p.numer} fer á {p.deild} og er {p.aldur}, liðinn tími er {env.now}")
                env.process(self.addP(p,False,False))
            except Interrupt:
                pass
    # Bætum nýjum sjúklingi við á deildina sína og látum hann bíða þar
    def addP(self,p,innritaður,endurkoma):
        self.fjoldi[(p.aldur,p.deild)] += 1
        if not innritaður:
            self.telja += 1
            self.amount += 1
            #print(f"fjöldi á spítala er núna {self.amount}, liðinn tími er {self.env.now}")
        if endurkoma:
            #print(self.endurkomur/self.telja)
            self.fjoldi["deildaskipti"][("heim",p.deild)] += 1
            self.endurkomur += 1
        wait = expovariate(1.0/self.fastar["Biðtímar"][(p.aldur,p.deild)])
        for deild in self.fastar["Upphafsstöður"]:
            fj_deild = sum(self.fjoldi[(age_grp,deild)] for age_grp in self.fastar["Aldurshópar"])
            load = fj_deild/((self.fastar["Starfsþörf"][deild][0]/self.fastar["Starfsþörf"][deild][1])*self.fjoldi["Læknar"][deild])
            while load > 1:
                self.fjoldi["Læknar"][deild] += self.fastar["Starfsþörf"][deild][1]
                load = fj_deild/((self.fastar["Starfsþörf"][deild][0]/self.fastar["Starfsþörf"][deild][1])*self.fjoldi["Læknar"][deild])
        #print(f"Sjúklingur númer {p.numer} á {p.deild} þarf að bíða þar í {wait}, liðinn tími er {self.env.now}")
        yield self.env.timeout(wait)
        yield self.env.process(p.updatePatient(self))
    # fjarlægjum sjúkling af deildinni prev
    def removeP(self,prev,p):
        #print(f"Sjúklingur númer {p.numer} fer af {prev} til {p.deild}, liðinn tími er {self.env.now}")
        self.amount -= 1
        self.fjoldi[(p.aldur,prev)] -= 1
        if p.deild == self.fastar["Stöður"][3]:
            self.discharged[p.numer] = p
    # Bíðum eftir sjúklingi sem hefur komið áður
    def homeGen(self,env,p_Dict):
        self.homePatientWait = True
        mean_arr = 10.0 #Breytum þessu, þetta á að vera meðaltal koma fólks á spítala sem hefur verið þar áður á dag
        wait = expovariate(mean_arr)
        yield env.timeout(wait)
        p_id = choice(list(p_Dict.keys()))
        p = p_Dict.pop(p_id)
        i_deild_upphaf = randomChoice(self.fastar["Upphafslíkur"])
        deild_upphaf = self.fastar["Upphafsstöður"][i_deild_upphaf]
        p.deild = deild_upphaf
        env.process(self.addP(p,False,True))
        self.homePatientWait = False
    #Bíðum eftir að upphitunartími sé búinn
    def upphitunWait(self):
        yield self.env.timeout(self.fastar["Upphitunartími"])
        self.upphitunFlag = True
        self.upphitun.succeed()

def interrupter(env,S,STOP,data,showSim,keys):
    yield S.upphitun
    for i in range(STOP):
        yield env.timeout(1)
        S.action.interrupt()
        for key in keys[2]:
            data[key].append(S.fjoldi[key])
        data["spitaliAmount"].append(S.amount)
        if S.amount > S.cap:
            data["dagar yfir cap"] += 1
        for deild in S.fastar["Upphafsstöður"]:
            data["Læknar"][deild] = S.fjoldi["Læknar"][deild]
        if showSim:
            d = {"fjöldi á spítala": [S.amount],"capacity": S.cap}
            df = DataFrame(d,index = [i])
            if i == 0:
                chart = line_chart(df)
            else:
                chart.add_rows(df)
            sleep(0.1)

def randomChoice(p):
    rnd = random()
    for i, w in enumerate(p):
        rnd -= w
        if rnd < 0:
            return i

def sim(showSim,simAttributes):
    #simAttributes inniheldur allar upplýsingar um forsendur hermuninnar
    #Ef maður vill sjá þróun fjölda fólks á spítalanum er showSim = True
    env = Environment()
    #Þurfum að endurstilla deildaskipti töfluna í hvert sinn sem sim er kallað
    KEYS_LEGU = [(simAttributes["Aldurshópar"][0],simAttributes["Stöður"][0]),
        (simAttributes["Aldurshópar"][1],simAttributes["Stöður"][0]),
        (simAttributes["Aldurshópar"][2],simAttributes["Stöður"][0])]
    KEYS_GONGU = [(simAttributes["Aldurshópar"][0],simAttributes["Stöður"][1]),
        (simAttributes["Aldurshópar"][1],simAttributes["Stöður"][1]),
        (simAttributes["Aldurshópar"][2],simAttributes["Stöður"][1])]
    simAttributes["deildaskipti"] = dict.fromkeys(simAttributes["deildaskipti"].keys(),0)
    #Upprunalegur fjöldi á spítalanum
    KEYS_TOT = KEYS_LEGU + KEYS_GONGU
    fjoldi = {keys : 0 for keys in KEYS_TOT}
    fjoldi["deildaskipti"] = simAttributes["deildaskipti"]
    fjoldi["Læknar"] = {deild : simAttributes["Starfsþörf"][deild][1] for deild in simAttributes["Upphafsstöður"]}
    #Gögnin sem sim skilar
    data = {keys : [] for keys in KEYS_TOT}
    data["spitaliAmount"] = []
    data["deildaskipti"] = {}
    data["dagar yfir cap"] = 0
    data["Læknar"] = {states: 0 for states in simAttributes["Upphafsstöður"]}
    STOP = simAttributes["STOP"]
    S = Spitali(fjoldi,env,simAttributes)
    env.process(interrupter(env,S,STOP,data,showSim,[KEYS_GONGU,KEYS_LEGU,KEYS_TOT]))
    env.run(until = STOP + simAttributes["Upphitunartími"])
    data["deildaskipti"] = S.fjoldi["deildaskipti"]
    data["heildarsjúklingar"] = S.telja
    #print(f"Heildar fjöldi fólks sem kom á spítalann alla hermunina er {S.telja}")
    return data

def hermHundur(totalData,simAttributes):
    KEYS_LEGU = [(simAttributes["Aldurshópar"][0],simAttributes["Stöður"][0]),
        (simAttributes["Aldurshópar"][1],simAttributes["Stöður"][0]),
        (simAttributes["Aldurshópar"][2],simAttributes["Stöður"][0])]
    KEYS_GONGU = [(simAttributes["Aldurshópar"][0],simAttributes["Stöður"][1]),
        (simAttributes["Aldurshópar"][1],simAttributes["Stöður"][1]),
        (simAttributes["Aldurshópar"][2],simAttributes["Stöður"][1])]
    KEYS_TOT = KEYS_GONGU + KEYS_LEGU
    L = simAttributes["Fjöldi hermana"]
    days = simAttributes["STOP"]-1
    stayData = []
    dagarYfirCap = []
    sankeyData = {key : [] for key in simAttributes["deildaskipti"]}
    for _ in range(L):
        data = sim(False,simAttributes)
        stayData.append(data["spitaliAmount"])
        for key in KEYS_TOT:
            totalData[key].append(np.sum(data[key])/days)
        for key in data["deildaskipti"]:
            sankeyData[key].append(data["deildaskipti"][key])
        for deild in simAttributes["Upphafsstöður"]:
            totalData["Læknar"][deild].append(data["Læknar"][deild])
        dagarYfirCap.append(data["dagar yfir cap"])
        totalData["heildarsjúklingar"].append(data["heildarsjúklingar"])
    totalData["Sankey"] = sankeyData
    stayData_arr = np.array(stayData)
    stayData_arr = np.transpose(stayData_arr)
    totalData["meðal lega"] = [np.mean(stayData_arr[row,:]) for row in range(days)]
    inter = []
    if L < 30:
        for i in range(days):
            inter.append(stats.t.interval(alpha=0.95,df = len(stayData_arr[i,:])-1, loc = totalData["meðal lega"][i],
                                          scale = stats.sem(stayData_arr[i,:])))
    else:
        for i in range(days):
            inter.append(stats.norm.interval(alpha=0.95,loc = totalData["meðal lega"][i],scale = stats.sem(stayData_arr[i,:])))
    totalData["CI"] = inter
    totalData["dagar yfir cap"] = dagarYfirCap
    return totalData
