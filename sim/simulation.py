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
    def __init__(self,aldur,deild,numer):
        self.aldur = aldur
        self.deild = deild
        self.timiSpitala = 0 # Þetta gæti verið gott í framtíð
        self.numer = numer # breyta fyrir aflúsun

class Deild:
    def __init__(self,env,S,nafn):
        self.env = env
        self.S = S
        self.nafn = nafn 
        self.fjoldiDag = {age : [0 for _ in range(S.fastar["Stop"]+1)] for age in S.fastar["AgeGroups"]}
        self.count = {age : 0 for age in S.fastar["AgeGroups"]}
        self.inni = 0
        self.maxInni = 0 # Breyta sem heldur utan um mestann fjölda fólks sem hefur verið á deildinni á hverjum tímapunkti

    def addP(self,p,innritaður,endurkoma,prev_deild):
        if innritaður:
            self.S.deildir[prev_deild].count[p.aldur] -= 1
            self.S.deildir[prev_deild].inni -= 1
        self.count[p.aldur] += 1
        self.inni += 1
        if self.inni > self.maxInni:
            self.maxInni = self.inni 
        if not innritaður:
            self.S.telja += 1
            self.S.amount += 1
            #print(f"fjöldi á spítala er núna {self.S.amount}, liðinn tími er {self.env.now}")
        if endurkoma:
            #print(self.endurkomur/self.telja)
            self.S.endurkomur += 1
        if self.S.upphitunFlag:
            self.fjoldiDag[p.aldur][self.S.dagar] += 1
        if self.nafn in self.S.fastar["WaitLognorm"]:
            sd = self.S.fastar["WaitLognorm"][self.nafn][p.aldur][1]
            mu = self.S.fastar["WaitLognorm"][self.nafn][p.aldur][0]
            wait = np.random.lognormal(mu,sd)
        if self.nafn in self.S.fastar["WaitUniform"]:
            wait = np.random.uniform(self.S.fastar["WaitUniform"][self.nafn][0],self.S.fastar["WaitUniform"][self.nafn][1])
        #print(f"Sjúklingur númer {p.numer} á {p.deild} þarf að bíða þar í {wait}, liðinn tími er {self.env.now}")
        yield self.env.timeout(wait)
        yield self.env.process(self.updatePatient(p))
    
    def updatePatient(self,p):
        i_deild = randomChoice(self.S.fastar["MoveProb"][(self.nafn,p.aldur)])
        newDeild = self.S.fastar["States"][i_deild]
        prev = p.deild
        p.deild = newDeild
        if self.S.upphitunFlag:
            self.S.fjoldi["Deildaskipti"][(self.nafn,newDeild)] += 1
        if newDeild in self.S.fastar["FinalState"]:
            self.removeP(p,prev)
        else:
            yield self.env.process(self.S.deildir[newDeild].addP(p,True,False,prev))
        
    def removeP(self,p,prev):
        #print(f"Sjúklingur númer {p.numer} fer af {prev} til {p.deild}, liðinn tími er {self.env.now}")
        self.S.amount -= 1
        self.count[p.aldur] -= 1
        self.inni -= 1
        if p.deild != self.S.fastar["States"][5]:
            self.S.discharged[p.numer] = p

class Kerfi:
    def __init__(self,fjoldi,env,simAttributes):
        self.fjoldi = fjoldi
        self.env = env
        self.fastar = simAttributes
        self.p_age = [(1.0/self.fastar["MeanWait"][age])/self.fastar["Lam"] for age in self.fastar["AgeGroups"]]
        self.telja = 0
        self.amount = 0 #sum(list(fjoldi.values()))
        self.discharged = {}
        self.deildir = {}
        self.endurkomur = 0
        self.dagar = 0
        deild_list = simAttributes["InitState"] + simAttributes["MedState"]
        for unit in deild_list:
            self.deildir[unit] = Deild(env,self,unit)
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
                wait = expovariate(self.fastar["Lam"])
                #print(f"Þurfum að bíða í {wait} langann tíma eftir næsta sjúkling, liðinn tími er {env.now}")
                yield env.timeout(wait)
                i_aldur = randomChoice(self.p_age)
                aldur = self.fastar["AgeGroups"][i_aldur]
                i_deild_upphaf = randomChoice(self.fastar["InitialProb"])
                deild_upphaf = self.fastar["InitState"][i_deild_upphaf]
                p = Patient(aldur,deild_upphaf,self.telja)
                #print(f"Sjúklingur númer {p.numer} fer á {p.deild} og er {p.aldur}, liðinn tími er {env.now}")
                env.process(self.deildir[deild_upphaf].addP(p,False,False,""))
            except Interrupt:
                self.dagar += 1

    # Bíðum eftir sjúklingi sem hefur komið áður
    # Þarf aðeins að breyta þessu, gæti verið gott að velja sjúkling með meiri líkur ef hann er á hjúkrun
    def homeGen(self,env,p_Dict):
        self.homePatientWait = True
        mean_arr = 10.0 #Breytum þessu, þetta á að vera meðaltal koma fólks á spítala sem hefur verið þar áður á dag
        wait = expovariate(mean_arr)
        yield env.timeout(wait)
        p_id = choice(list(p_Dict.keys()))
        p = p_Dict.pop(p_id)
        #print(self.endurkomur/self.telja)
        self.endurkomur += 1
        i_deild_upphaf = randomChoice(self.fastar["InitialProb"])
        deild_upphaf = self.fastar["InitState"][i_deild_upphaf]
        self.fjoldi["Deildaskipti"][(p.deild,deild_upphaf)] += 1
        p.deild = deild_upphaf
        env.process(self.deildir[deild_upphaf].addP(p,False,True,""))
        self.homePatientWait = False
    #Bíðum eftir að upphitunartími sé búinn
    def upphitunWait(self):
        yield self.env.timeout(self.fastar["WarmupTime"])
        self.upphitunFlag = True
        self.upphitun.succeed()

def CalcNumJobs(S,simAttributes):
    deildir = simAttributes["InitState"] + simAttributes["MedState"]
    job_demand = {key : 0 for key in simAttributes["JobDemand"]}
    for state in deildir:
        for job in S.fastar["Jobs"]:
            load = ceil(S.deildir[state].maxInni/S.fastar["JobDemand"][(state,job)][0])
            job_demand[(state,job)] = load*S.fastar["JobDemand"][(state,job)][1]
    return job_demand

def interrupter(env,S,Stop,data,showSim,ageGroups):
    yield S.upphitun
    for i in range(Stop):
        yield env.timeout(1)
        S.action.interrupt()
        for key in S.fastar["Keys"]:
            data[key].append(S.deildir[key[1]].count[key[0]])
        data["leguAmount"].append(S.deildir["legudeild"].inni)
        if showSim:
            s = sum([S.deildir["legudeild"].fjoldiDag[age][i] for age in ageGroups])
            d = {"fjöldi sem kom á legudeild": [s]}
            df = DataFrame(d,index = [i])
            if i == 0:
                chart = line_chart(df)
            else:
                chart.add_rows(df)
            sleep(0.1)

# Fall sem skilar tölu milli 0 og len(p)-1 með líkindadreifingu gefna í p
# sum(p) þarf að vera 1
def randomChoice(p):
    rnd = random()
    for i, w in enumerate(p):
        rnd -= w
        if rnd < 0:
            return i

def HermunInit(simAttributes):
    lyklar = simAttributes["Keys"]
    simAttributes["Deildaskipti"] = dict.fromkeys(simAttributes["Deildaskipti"].keys(),0)
    fjoldi = {}
    fjoldi["Deildaskipti"] = simAttributes["Deildaskipti"]
    #Gögnin sem sim skilar
    data = {keys : [] for keys in lyklar}
    data["leguAmount"] = []
    data["Deildaskipti"] = {}
    data["dagar yfir cap"] = 0
    data["Læknar"] = {key : 0 for key in list(simAttributes["JobDemand"].keys())}
    data["Fjöldi á dag"] = {state : {} for state in simAttributes["InitState"]+simAttributes["MedState"]}
    return [data,fjoldi]

# Fall sem framkvæmir eina hermun
def sim(showSim,simAttributes):
    [data,fjoldi] = HermunInit(simAttributes)
    env = Environment()
    S = Kerfi(fjoldi,env,simAttributes)
    env.process(interrupter(env,S,simAttributes["Stop"],data,showSim,simAttributes["AgeGroups"]))
    env.run(until = simAttributes["Stop"] + simAttributes["WarmupTime"]+1)
    data["Deildaskipti"] = S.fjoldi["Deildaskipti"]
    data["heildarsjúklingar"] = S.telja
    for state in simAttributes["InitState"]+simAttributes["MedState"]:
        data["Fjöldi á dag"][state] = S.deildir[state].fjoldiDag
    #print(f"Heildar fjöldi fólks sem kom á spítalann alla hermunina er {S.telja}")
    data["Læknar"] = CalcNumJobs(S,simAttributes)
    return data

# Fall sem hermir kerfið L sinnum
def hermHundur(totalData,simAttributes):
    lyklar = simAttributes["Keys"]
    L = simAttributes["SimAmount"]
    days = simAttributes["Stop"]
    stayData = []
    dagarYfirCap = []
    sankeyData = {key : [] for key in simAttributes["Deildaskipti"]}
    for _ in range(L):
        data = sim(False,simAttributes)
        stayData.append(data["leguAmount"])
        for key in lyklar:
            totalData[key].append(np.sum(data[key])/days)
        for key in data["Deildaskipti"]:
            sankeyData[key].append(data["Deildaskipti"][key])
        for key in simAttributes["JobDemand"]:
            totalData["Læknar"][key].append(data["Læknar"][key])
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