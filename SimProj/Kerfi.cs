using SimSharp;
/* 
    Þessi class hermir kerfið í heild
 */

namespace SimProj;

public class Kerfi
{
    private Simulation env;
    public SimAttribs fastar;
    private List<double> p_age = new List<double>();
    public int telja;
    public int amount;
    public int Dagur;
    public Dictionary<string, Deild> deildir = new Dictionary<string, Deild>();
    private Process action;
    private Event upphitun;
    private MathNet.Numerics.Distributions.Exponential arrive;
    public Kerfi(Simulation envment, SimAttribs simAttributes) {
        env = envment;
        fastar = simAttributes;
        foreach(string age_grp in fastar.AgeGroups)
        {
            p_age.Add((1.0 / fastar.MeanWait[age_grp]) / fastar.Lam);
        }
        telja = 0;
        Dagur = 0;
        amount = 0;
        upphitun = new Event(env);
        arrive = new MathNet.Numerics.Distributions.Exponential(fastar.Lam);
        CreateDeildir();
        action = env.Process(patientGen(env));
        env.Process(upphitunWait());
    }
    private IEnumerable<Event> patientGen(Simulation env)
    {
        while (true)
        {
            if (!env.ActiveProcess.HandleFault())
            {
                double wait = arrive.Sample();
                yield return env.TimeoutD(wait);
                int i_aldur = Helpers.randomChoice(p_age);
                string aldur = fastar.AgeGroups[i_aldur];
                int i_deild_upphaf = Helpers.randomChoice(fastar.InitialProb);
                string deild_upphaf = fastar.InitState[i_deild_upphaf];
                Patient p = new Patient(aldur, deild_upphaf, telja);
                env.Process(deildir[deild_upphaf].addP(p, false, ""));
            }
            else { Dagur++; }
        }
    }
    private void CreateDeildir()
    {
        var deild_list = fastar.InitState.Concat(fastar.MedState);
        foreach (string unit in deild_list)
        {
            deildir[unit] = new Deild(env, unit, fastar, this);
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
            foreach ((string,string) keyArr in data.deildAgeAmount.Keys)
            {
                data.deildAgeAmount[keyArr].Add(deildir[keyArr.Item2].dataDeild.fjoldiInni[keyArr.Item1]);
            }
            data.LeguAmount.Add(deildir["legudeild"].dataDeild.inni);
        }
    }
    private IEnumerable<Event> upphitunWait()
    {
        yield return env.TimeoutD(fastar.WarmupTime);
        Run.upphitunFlag = true;
        upphitun.Succeed();
    }
}