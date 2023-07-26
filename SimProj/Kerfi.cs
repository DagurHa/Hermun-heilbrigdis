using SimSharp;

/* 
    Þessi class hermir kerfið í heild
 */

namespace SimProj;

public class Kerfi
{
    public Dictionary<string, DeildInfo> data = new Dictionary<string, DeildInfo>();
    private Simulation env;
    public SimAttribs fastar;
    private List<double> p_age = new List<double>();
    public int telja;
    public int amount;
    public int Dagur;
    private Dictionary<int,Patient> discharged = new Dictionary<int,Patient>();
    public Dictionary<string, Deild> deildir = new Dictionary<string, Deild>();
    public int endurkomur;
    private Process action;
    private Event upphitun;
    private bool homePatientWait;
    private MathNet.Numerics.Distributions.Exponential arrive;
    public Kerfi(Simulation envment, SimAttribs simAttributes) {
        env = envment;
        fastar = simAttributes;
        foreach(string age_grp in fastar.AgeGroups)
        {
            p_age.Add((1.0 / fastar.MeanExp[age_grp]) / fastar.Lam);
        }
        foreach (string state in fastar.States) { data[state] = new DeildInfo(fastar); }
        telja = 0;
        Dagur = 0;
        amount = 0;
        endurkomur = 0;
        homePatientWait = false;
        upphitun = new Event(env);
        arrive = new MathNet.Numerics.Distributions.Exponential(1.0/fastar.Lam);
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
                if (discharged.Count > 0 & !homePatientWait)
                {
                    //env.Process(homeGen(env, discharged));
                }
                double wait = arrive.Sample();
                File.AppendAllText(Run.pth, $"Þurfum að bíða í {wait} langann tima eftir næsta sjukling" + System.Environment.NewLine);
                yield return env.TimeoutD(wait);
                int i_aldur = Helpers.randomChoice(p_age);
                string aldur = fastar.AgeGroups[i_aldur];
                int i_deild_upphaf = Helpers.randomChoice(fastar.InitialProb);
                string deild_upphaf = fastar.InitState[i_deild_upphaf];
                Patient p = new Patient(aldur, deild_upphaf, telja);
                File.AppendAllText(Run.pth, $"Sjúklingur numer {p.Numer} fer á {p.Deild} og er {p.Aldur}, liðinn tími er {env.NowD}" + System.Environment.NewLine);
                env.Process(deildir[deild_upphaf].addP(p, false, false, ""));
            }
            else 
            {
                File.AppendAllText(Run.pth, "Interrupted!" + System.Environment.NewLine);
                Dagur++;
            }
        }
    }
    private void CreateDeildir()
    {
        var deild_list = fastar.InitState.Concat(fastar.MedState);
        foreach (string unit in deild_list)
        {
            deildir[unit] = new Deild(env, unit, fastar, data[unit], this);
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
                string[] keyArr = { key_list[0], key_list[1] };
                data.deildAgeAmount[keyArr].Add(deildir[key_list[1]].dataDeild.fjoldiInni[key_list[0]]);
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