import numpy as np
from random import expovariate, random
from time import sleep
from pandas import DataFrame
from streamlit import line_chart
from simpy import Environment,Interrupt

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
        new_deild = S.fastar["Stöður"][i_deild]
        self.deild = new_deild
        if S.upphitunFlag:
            S.fjoldi["deildaskipti"][(prev,self.deild)] += 1
        if self.deild == S.fastar["Stöður"][2] or self.deild == S.fastar["Stöður"][3]:
            S.removeP(prev,self)
        else:
            if prev == S.fastar["Stöður"][0]:
                S.fjoldi[self.aldur] -= 1
            yield self.env.process(S.addP(self,True))

class Deild:
    def __init__(self,nafn):
        self.nafn = nafn
        self.fjoldi = 0
    def addToDeild(self):
        self.fjoldi += 1
    def getFjoldi(self):
        return self.fjoldi

class Spitali:
    def __init__(self,fjoldi,env,simAttributes):
        self.fjoldi = fjoldi
        self.env = env
        self.fastar = simAttributes
        self.cap = self.fastar["CAP"]
        self.p_age = [(1.0/self.fastar["meðalbið"][age])/self.fastar["lambda"] for age in self.fastar["Aldurshópar"]]
        self.telja = 0
        self.amount = 0 #sum(list(fjoldi.values()))
        self.action = env.process(self.patientGen(env))
        self.upphitun = env.event()
        env.process(self.upphitunWait())
        self.upphitunFlag = False
    def patientGen(self,env):
        while True:
            try:
                wait = expovariate(self.fastar["lambda"])
                #print(f"Þurfum að bíða í {wait} langann tíma eftir næsta sjúkling, liðinn tími er {env.now}")
                yield env.timeout(wait)
                i_aldur = randomChoice(self.p_age)
                aldur = self.fastar["Aldurshópar"][i_aldur]
                i_deild_upphaf = randomChoice(self.fastar["Upphafslíkur"])
                deild_upphaf = self.fastar["Upphafsstöður"][i_deild_upphaf]
                p = Patient(aldur,env,deild_upphaf,self.telja)
                #print(f"Sjúklingur númer {p.numer} fer á {p.deild} og er {p.aldur}, liðinn tími er {env.now}")
                env.process(self.addP(p,False))
            except Interrupt:
                pass
    # Bætum nýjum sjúklingi við á deildina sína og látum hann bíða þar
    def addP(self,p,innritaður):
        if p.deild == self.fastar["Stöður"][0]:
            self.fjoldi[p.aldur] += 1
        if not innritaður:
            self.telja += 1
            self.amount += 1
            #print(f"fjöldi á spítala er núna {self.amount}, liðinn tími er {self.env.now}")
        wait = expovariate(1.0/self.fastar["Biðtímar"][(p.aldur,p.deild)])
        #print(f"Sjúklingur númer {p.numer} á {p.deild} þarf að bíða þar í {wait}, liðinn tími er {self.env.now}")
        yield self.env.timeout(wait)
        yield self.env.process(p.updatePatient(self))
    # fjarlægjum sjúkling af deildinni prev
    def removeP(self,prev,p):
        #print(f"Sjúklingur númer {p.numer} fer af {prev} til {p.deild}, liðinn tími er {self.env.now}")
        self.amount -= 1
        if prev == self.fastar["Stöður"][0]:
            self.fjoldi[p.aldur] -= 1
    #Bíðum eftir að upphitunartími sé búinn
    def upphitunWait(self):
        yield self.env.timeout(self.fastar["Upphitunartími"])
        self.upphitunFlag = True
        self.upphitun.succeed()

def interrupter(env,S,STOP,data,showSim):
    yield S.upphitun
    for i in range(STOP):
        yield env.timeout(1)
        S.action.interrupt()
        for age_group in S.fastar["Aldurshópar"]:
            data[age_group].append(S.fjoldi[age_group])
        data["spitaliAmount"].append(S.amount)
        if S.amount > S.cap:
            data["dagar yfir cap"] += 1
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
    simAttributes["deildaskipti"] = dict.fromkeys(simAttributes["deildaskipti"].keys(),0)
    #Upprunalegur fjöldi á spítalanum
    fjoldi = {
        simAttributes["Aldurshópar"][0] : 0,
        simAttributes["Aldurshópar"][1] : 0,
        simAttributes["Aldurshópar"][2] : 0,
        "deildaskipti" : simAttributes["deildaskipti"]
    }
    #Gögnin sem sim skilar
    data = {
        simAttributes["Aldurshópar"][0] : [],
        simAttributes["Aldurshópar"][1] : [],
        simAttributes["Aldurshópar"][2] : [],
        "spitaliAmount" : [],
        "deildaskipti" : {},
        "dagar yfir cap" : 0
    }
    STOP = simAttributes["STOP"]
    S = Spitali(fjoldi,env,simAttributes)
    env.process(interrupter(env,S,STOP,data,showSim))
    env.run(until = STOP + simAttributes["Upphitunartími"])
    data["deildaskipti"] = S.fjoldi["deildaskipti"]
    #print(f"Heildar fjöldi fólks sem kom á spítalann alla hermunina er {S.telja}")
    return data

def hermHundur(totalData,simAttributes):
    L = simAttributes["Fjöldi hermana"]
    days = simAttributes["STOP"]-1
    stayData = []
    dagarYfirCap = []
    sankeyData = {key : [] for key in simAttributes["deildaskipti"]}
    for _ in range(L):
        data = sim(False,simAttributes)
        stayData.append(data["spitaliAmount"])
        for key in simAttributes["Aldurshópar"]:
            totalData[key].append(np.sum(data[key])/days)
        for key in data["deildaskipti"]:
            sankeyData[key].append(data["deildaskipti"][key])
        dagarYfirCap.append(data["dagar yfir cap"])
    totalData["Sankey"] = sankeyData
    stayData_arr = np.array(stayData)
    stayData_arr = np.transpose(stayData_arr)
    totalData["meðal lega"] = [np.sum(stayData_arr[row,:])/L for row in range(days)]
    totalData["mesta lega"] = [np.amax([stayData_arr[row,j] for j in range(L) 
                                         if stayData_arr[row,j] <= 0.95*np.amax(stayData_arr[row,:])]) for row in range(days)]
    totalData["minnsta lega"] = [np.amin([stayData_arr[row,j] for j in range(L) 
                                         if stayData_arr[row,j] >= 1.05*np.amin(stayData_arr[row,:])]) for row in range(days)]
    totalData["dagar yfir cap"] = dagarYfirCap
    return totalData
