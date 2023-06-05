import simpy as sp
import random
import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px

inpatient_arrival = []
outpatient_arrival = []
pts = []
arrival_rates = {'Young':1.0/0.2,'Middle-aged':1.0/0.4,'Old':1.0/0.6}
min_summa = 1.0/0.2+1.0/0.4+1.0/0.6

class Patient:
    def __init__(self, id, age, unit):
        self.id = id
        self.age = age
        self.unit = unit

class Hospital:
    def __init__(self, env):
        self.env = env
        self.outpatient_units = sp.Resource(env,100)
        self.inpatient_units = sp.Resource(env,100)
        self.num_patients_outpatient = 0
        self.num_patients_inpatient = 0
        self.action = env.process(self.patient_arrival())

    def assign_unit(self, patient):
        if random.random() < 0.7:
            with self.outpatient_units.request() as request:
                yield request # Patient arrived at outpatient unit
                self.num_patients_outpatient += 1
                patient.unit = "Outpatient"
                #print(f'{patient.id} ({patient.age}) assigned to outpatient unit')

                yield self.env.timeout(0.3)  # Treatment time
                #print(f'{patient.id} ({patient.age}) discharged from outpatient unit')
                self.num_patients_outpatient -= 1
        else:
            with self.inpatient_units.request() as request:
                yield request # Patient arrived to inpatient unit
                self.num_patients_inpatient += 1
                patient.unit = "Inpatient"
                #print(f'{patient.id} ({patient.age}) assigned to inpatient unit')

                yield self.env.timeout(1)  # Treatment time
                #print(f'{patient.id} ({patient.age}) discharged from inpatient unit')
                self.num_patients_inpatient -= 1

    def patient_arrival(self):
        while True:
            age_group = np.random.choice(["Young","Middle-aged","Old"],
                                         1,
                                         p=[(1.0/0.6)/min_summa,(1.0/0.4)/min_summa,(1.0/0.2)/min_summa])
            #age_group = random.choices(
            #    population=['Young', 'Middle-aged', 'Old'],
            #    cum_weights=[(1.0/0.2)/min_summa, (1.0/0.4)/min_summa, (1.0/0.6)/min_summa])
            try:    
                yield self.env.timeout(random.expovariate(min_summa))  # Patient arrival rate
            except sp.Interrupt:
                print("Process interrupted at time ",env.now)
                print("Number of patients in outpatient unit:", hospital.num_patients_outpatient)
                print("Number of patients in inpatient unit:", hospital.num_patients_inpatient)
            patient = Patient(f'Patient-{self.env.now}', age_group,"")
            pts.append(patient)
            self.env.process(self.assign_unit(patient))
    
def the_interrupter(env,Hospital):
    yield env.timeout(30)
    Hospital.action.interrupt()
    yield env.timeout(30)
    Hospital.action.interrupt()

# Run 
env = sp.Environment()
hospital = Hospital(env)

env.process(the_interrupter(env,hospital))
env.run(until=100)
print("Process complete at time ",env.now)
print("Current left in Outpatient unit: ",hospital.num_patients_outpatient)
print("Current left in Inpatient unit: ",hospital.num_patients_inpatient)



ungur = np.zeros(2)
middle = np.zeros(2)
old = np.zeros(2)
inp = 0
outp = 0

for p in pts:
    if p.age == "Young" and p.unit == "Inpatient":
        ungur[0] += 1
    elif p.age == "Young" and p.unit == "Outpatient":
        ungur[1] += 1
    elif p.age == "Middle-aged" and p.unit == "Inpatient":
        middle[0] += 1
    elif p.age == "Middle-aged" and p.unit == "Outpatient":
        middle[1] += 1
    elif p.age == "Old" and p.unit == "Inpatient":
        old[0] += 1
    else:
        old[1] += 1
    if p.unit == "Outpatient":
        outp +=1
    else:
        inp +=1

print(f"Number of Young/Middle-aged/Old arrivals in the Inpatient unit: {ungur[0]}/{middle[0]}/{old[0]}")
print(f"Number of Young/Middle-aged/Old arrivals in the Outpatient unit: {ungur[1]}/{middle[1]}/{old[1]}")
print(f"Total no. of arrivals in the Outpatient/Inpatient unit: {outp}/{inp}")

ungur = [ungur[0], ungur[1]]  # Number of young patients: [Inpatient, Outpatient]
middle = [middle[0], middle[1]]  # Number of middle-aged patients: [Inpatient, Outpatient]
old = [old[0], old[1]]  # Number of old patients: [Inpatient, Outpatient]

df = pd.DataFrame(
    {
        "Age group": ["Young", "Middle-aged", "Old", "Young", "Middle-aged", "Old"],
        "Unit": ["Inpatient", "Inpatient", "Inpatient", "Outpatient", "Outpatient", "Outpatient"],
        "No. of patients": ungur + middle + old,
    }
)

color_mapping = {"Inpatient": "red", "Outpatient": "blue"}

fig = px.bar(
    df,
    x="Age group",
    y="No. of patients",
    color="Unit",
    color_discrete_map=color_mapping,
    barmode="group",
    labels={"Age group": "Age group", "No. of patients": "No. of patients"},
)
st.write("# Patient arrivals")
st.plotly_chart(fig)

