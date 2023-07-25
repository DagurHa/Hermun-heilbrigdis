/* Þessi class hermir deildir kerfisins 
 * 
 */
using SimSharp;

namespace SimProj;
public class Deild
{
    public DeildInfo dataDeild;
    public SimAttribs simAttribs;
    private string nafn;
    private Simulation env;
    private Dictionary<string,MathNet.Numerics.Distributions.LogNormal> waitLognorm = new Dictionary<string, MathNet.Numerics.Distributions.LogNormal>();
    private MathNet.Numerics.Distributions.ContinuousUniform WaitUnif;
    private double wait = 0;
    private readonly IEnumerable<int>? deildnr;
    public Deild(Simulation envment, string Nafn, SimAttribs SimAttributes,DeildInfo DataDeild)
    {
        env = envment;
        nafn = Nafn;
        simAttribs = SimAttributes;
        dataDeild = DataDeild;
        if(simAttribs.WaitLognorm.ContainsKey(nafn)){
            foreach (string age_grp in simAttribs.AgeGroups)
            {
                //Þarf að tjekka hvort sé verið að nota retta mu og sd
                MathNet.Numerics.Distributions.LogNormal lgnrm = new MathNet.Numerics.Distributions.LogNormal(simAttribs.WaitLognorm[nafn][age_grp][0], simAttribs.WaitLognorm[nafn][age_grp][1]);
                waitLognorm[age_grp] = lgnrm;
            }
        }
        if (simAttribs.WaitUniform.ContainsKey(nafn))
        {
            WaitUnif = new MathNet.Numerics.Distributions.ContinuousUniform(simAttribs.WaitUniform[nafn][0], simAttribs.WaitUniform[nafn][1]);
            deildnr = Enumerable.Range(0, simAttribs.States.Count);
        }
    }
    public IEnumerable<Event> addP(Patient p, bool innrit, bool endurkoma, string prev_deild)
    {
        if (innrit)
        {
            Run.kerfi.deildir[prev_deild].dataDeild.fjoldiInni[p.Aldur]--;
            Run.kerfi.deildir[prev_deild].dataDeild.inni--;
        }
        else
        {
            Run.kerfi.telja++;
            Run.kerfi.amount++;
        }
        if (endurkoma) { Run.kerfi.endurkomur++; }
        dataDeild.fjoldiInni[p.Aldur]++;
        dataDeild.inni++;
        if (dataDeild.inni > dataDeild.maxInni){ dataDeild.maxInni = dataDeild.inni; }
        if (simAttribs.WaitLognorm.ContainsKey(nafn)){ wait = waitLognorm[p.Aldur].Sample(); }
        else if (simAttribs.WaitUniform.ContainsKey(nafn)){ wait = WaitUnif.Sample(); }
        yield return env.TimeoutD(wait);
        yield return env.Process(updatePatient(p));
    }
    public IEnumerable<Event> updatePatient(Patient p)
    {
        int i_deild = Helpers.randomChoice(simAttribs.MoveProb[(nafn,p.Aldur)]);
        string newDeild = simAttribs.States[i_deild];
        string prev = p.Deild;
        p.Deild = newDeild;
        if (Run.upphitunFlag)
        {
            dataDeild.deildSkipt[Helpers.getDeildnr(prev, simAttribs.States)]++;
        }
        if (simAttribs.FinalState.Contains(newDeild)) { removeP(p); }
        else
        {
            yield return env.Process(Run.kerfi.deildir[newDeild].addP(p,true,false,prev));
        }
    }
    public void removeP(Patient p)
    {
        dataDeild.inni--;
        dataDeild.fjoldiInni[p.Aldur]--;
        if (p.Deild != simAttribs.States[5])
        {

        }
    }
}

