import simpy as sp
import random
import numpy as np

inpatient_arrival = []
outpatient_arrival = []
pts = []
arrival_rates = {'Young':0.2,'Middle-aged':0.4,'Old':0.6} 

class Patient:
    def __init__(self, id, age):
        self.id = id
        self.age = age

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
                #print(f'{patient.id} ({patient.age}) assigned to outpatient unit')

                yield self.env.timeout(random.expovariate(0.02))  # Treatment time
                #print(f'{patient.id} ({patient.age}) discharged from outpatient unit')
                #self.num_patients_outpatient -= 1
        else:
            with self.inpatient_units.request() as request:
                yield request # Patient arrived to inpatient unit
                self.num_patients_inpatient += 1
                #print(f'{patient.id} ({patient.age}) assigned to inpatient unit')

                yield self.env.timeout(0.1)  # Treatment time
                #print(f'{patient.id} ({patient.age}) discharged from inpatient unit')
                #self.num_patients_inpatient -= 1

    def patient_arrival(self):
        while True:
            age_group = random.choices(
                population=['Young', 'Middle-aged', 'Old'],
                weights=[0.2, 0.3, 0.5])[0]
            try:    
                yield self.env.timeout(random.expovariate(arrival_rates[age_group]))  # Patient arrival rate
            except sp.Interrupt:
                print("Process interrupted at time ",env.now)
                print("Number of patients in outpatient unit:", hospital.num_patients_outpatient)
                print("Number of patients in inpatient unit:", hospital.num_patients_inpatient)
            patient = Patient(f'Patient-{self.env.now}', age_group)
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
print("Outpatient unit: ",hospital.num_patients_outpatient)
print("Inpatient unit: ",hospital.num_patients_inpatient)


"""
timeout1 = env.timeout(25)
timeout2 = env.timeout(50)
timeout3 = env.timeout(75)
try:
    env.run(until=timeout1)
    print("Simulation interrupted at time:", env.now)
    print("Number of patients in outpatient unit:", hospital.num_patients_outpatient)
    print("Number of patients in inpatient unit:", hospital.num_patients_inpatient)
except sp.Interrupt:
    print("Simulation interrupted at time:", env.now)
    print("Number of patients in outpatient unit:", hospital.num_patients_outpatient)
    print("Number of patients in inpatient unit:", hospital.num_patients_inpatient)

try:
    env.run(until=timeout2)
    print("Simulation interrupted at time:", env.now)
    print("Number of patients in outpatient unit:", hospital.num_patients_outpatient)
    print("Number of patients in inpatient unit:", hospital.num_patients_inpatient)
except sp.Interrupt:
    print("Simulation interrupted at time:", env.now)
    print("Number of patients in outpatient unit:", hospital.num_patients_outpatient)
    print("Number of patients in inpatient unit:", hospital.num_patients_inpatient)

try:
    env.run(until=timeout3)
    print("Simulation interrupted at time:", env.now)
    print("Number of patients in outpatient unit:", hospital.num_patients_outpatient)
    print("Number of patients in inpatient unit:", hospital.num_patients_inpatient)
except sp.Interrupt:
    print("Simulation interrupted at time:", env.now)
    print("Number of patients in outpatient unit:", hospital.num_patients_outpatient)
    print("Number of patients in inpatient unit:", hospital.num_patients_inpatient)

env.run(until=100)
print("Simulation complete at time: ",env.now)
print("Number of arrivals in outpatient unit: ",hospital.num_patients_outpatient)
print("Number of arrivals in inpatient unit: ",hospital.num_patients_inpatient)
"""

ungur = 0
middle = 0
old = 0

for p in pts:
    if p.age == "Young":
        ungur += 1
    elif p.age == "Middle-aged":
        middle += 1
    else:
        old +=1

#print(f"Number of Young/Middle-aged/Old patients: {ungur}/{middle}/{old}")
