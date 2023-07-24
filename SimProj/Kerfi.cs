using SimSharp;
using static SimSharp.Distributions;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Runtime.CompilerServices;

/* 
    Þessi class hermir kerfið í heild
 */

namespace SimProj;

public class Kerfi
{
    private Dictionary<string, DeildInfo> data = new Dictionary<string, DeildInfo>();
    private Simulation env;
    private SimAttribs fastar;
    private List<double> p_age = new List<double>();
    private int telja;
    private int amount;
    private Dictionary<int,Patient> discharged = new Dictionary<int,Patient>();
    private Dictionary<string, Deild> deildir = new Dictionary<string, Deild>();
    private int endurkomur;
    private Process action;
    private Event upphitun;
    private bool homePatientWait;
    private IDistribution<double> arrive;
    public Kerfi(Simulation envment, SimAttribs simAttributes) {
        env = envment;
        fastar = simAttributes;
        foreach(string age_grp in fastar.AgeGroups)
        {
            p_age.Add((1.0 / fastar.MeanExp[age_grp]) / fastar.Lam);
        }
        telja = 0;
        amount = 0;
        endurkomur = 0;
        homePatientWait = false;
        arrive = EXP(fastar.Lam);
        CreateDeildir();
        action = env.Process(patientGen(env));
        env.Process(upphitunWait());
    }
    private IEnumerable<Event> patientGen(Simulation env)
    {
        while (true)
        {
            if(discharged.Count >0 & !homePatientWait)
            {
                //env.Process(homeGen(env, discharged));
            }
            yield return env.TimeoutD(arrive);
            int i_aldur = Helpers.randomChoice(p_age);
            string aldur = fastar.AgeGroups[i_aldur];
            int i_deild_upphaf = Helpers.randomChoice(fastar.InitialProb);
            string deild_upphaf = fastar.InitState[i_deild_upphaf];
            Patient p = new Patient(aldur, deild_upphaf, telja);
            env.Process(deildir[deild_upphaf].addP(p, false, false, ""));
        }
    }
    private void CreateDeildir()
    {
        var deild_list = fastar.InitState.Concat(fastar.MedState);
        foreach (string unit in deild_list)
        {
            deildir[unit] = new Deild(env, unit, fastar);
        }
    }
    public IEnumerable<Event> interrupter(DataFinal data)
    {
        int STOP = fastar.Stop;
        yield return upphitun;
        foreach(int i in Enumerable.Range(0, STOP))
        {
            yield return env.TimeoutD(1.0);
            action.Interrupt();
            foreach (List<string> key_list in fastar.Keys)
            {
                data.deildAgeAmount[(key_list[0], key_list[1])].Add(deildir[key_list[1]].dataDeild.fjoldiInni[key_list[0]]);
            }
        }
    }
    private IEnumerable<Event> upphitunWait()
    {
        yield return env.TimeoutD(fastar.WarmupTime);
        Run.upphitunFlag = true;
        upphitun.Succeed();
    }
}
