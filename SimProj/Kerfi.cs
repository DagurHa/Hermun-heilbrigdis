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
    private bool upphitunFlag;
    private bool homePatientWait;
    private IDistribution<TimeSpan> arrive;
    public Kerfi(Simulation envment, SimAttribs simAttributes) {
        env = envment;
        fastar = simAttributes;
        foreach(string age_grp in fastar.age_grps)
        {
            p_age.Add((1.0 / fastar.meanExp[age_grp]) / fastar.lam);
        }
        telja = 0;
        amount = 0;
        endurkomur = 0;
        action = env.Process(patientGen(env));
        upphitunFlag = false;
        homePatientWait = false;
        arrive = EXP(TimeSpan.FromHours(fastar.lam));
        CreateDeildir();
    }
    private IEnumerable<Event> patientGen(Simulation env)
    {
        while (true)
        {
            if(discharged.Count >0 & !homePatientWait)
            {
                //env.Process(homeGen(env, discharged));
            }
            yield return env.Timeout(arrive);
            int i_aldur = Helpers.randomChoice(p_age);
            string aldur = fastar.age_grps[i_aldur];
            int i_deild_upphaf = Helpers.randomChoice(fastar.initialProb);
            string deild_upphaf = fastar.initState[i_deild_upphaf];
            Patient p = new Patient(aldur, deild_upphaf, telja);
            env.Process(deildir[deild_upphaf].addP(p, false, false, ""));
        }
    }
    private void CreateDeildir()
    {
        var deild_list = fastar.initState.Concat(fastar.medState);
        foreach (string unit in deild_list)
        {
            deildir[unit] = new Deild(env, unit, fastar);
        }
    }
    public IEnumerable<Event> interrupter(DataFinal data)
    {
        int STOP = fastar.stop;
        yield return upphitun;
        foreach(int i in Enumerable.Range(0, STOP))
        {
            yield return env.TimeoutD(1.0);
            action.Interrupt();
            foreach((string,string) key in fastar.keys)
            {
                data.deildAgeAmount[key].Add(deildir[key.Item2].dataDeild.fjoldiInni[key.Item1]);
            }
            if (fastar.showSim)
            {
                /*
                 Hér þarf að setja ehv pípu yfir í python til að færa gögn in real time
                 */
            }
        }
    }
}
