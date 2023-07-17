/* Þessi class hermir deildir kerfisins 
 * 
 */
using SimSharp;
using static SimSharp.Distributions;

namespace SimProj;
public class Deild
{
    private IRandom rng;
    public DeildInfo dataDeild;
    public SimAttribs simAttribs;
    //private Kerfi S; //Sleppa þessu?
    private string nafn;
    private Simulation env;
    private Dictionary<string,LogNormal> waitLognorm = new Dictionary<string, LogNormal>();
    private Uniform waitUnif;
    private double wait = 0;
    private IEnumerable<int> deildnr;
    public Deild(Simulation envment, /*Kerfi kerfi,*/ string Nafn, SimAttribs SimAttributes)
    {
        env = envment;
        //S = kerfi;
        nafn = Nafn;
        simAttribs = SimAttributes;
        dataDeild = new DeildInfo(simAttribs);
        foreach(string age_grp in simAttribs.age_grps)
        {
            LogNormal lgnrm = new LogNormal(simAttribs.waitLognorm[nafn][age_grp].Item1, simAttribs.waitLognorm[nafn][age_grp].Item2);
            waitLognorm[age_grp] = lgnrm;
        }
        Uniform waitUnif = new Uniform(simAttribs.waitUniform[nafn].Item1, simAttribs.waitUniform[nafn].Item2);
        deildnr = Enumerable.Range(0, simAttribs.states.Count);
    }
    public IEnumerable<Event> addP(Patient p, bool innrit, bool endurkoma, string prev_deild)
    {
        dataDeild.fjoldiInni[p.Aldur]++;
        dataDeild.inni++;
        if (dataDeild.inni > dataDeild.maxInni){ dataDeild.maxInni = dataDeild.inni; }
        if (simAttribs.waitLognorm.ContainsKey(nafn))
        {
            wait = waitLognorm[p.Aldur].Sample(rng);
        }
        else if (simAttribs.waitUniform.ContainsKey(nafn))
        {
            wait = waitUnif.Sample(rng);
        }
        yield return env.TimeoutD(wait);
        yield return env.Process(updatePatient(p));
    }
    public IEnumerable<Event> updatePatient(Patient p)
    {
        int i_deild = Helpers.randomChoice(simAttribs.moveProb[(nafn,p.Aldur)]);
        string newDeild = simAttribs.states[i_deild];
        string prev = p.Deild;
        p.Deild = newDeild;
        if (Run.upphitunFlag)
        {
            dataDeild.deildSkipt[Helpers.getDeildnr(prev, simAttribs.states)]++;
        }
        if (simAttribs.finalState.Contains(newDeild)) { removeP(p); }
        else
        {
            //yield return env.Process(//addP á nýju deild)
        }
        yield return env.TimeoutD(1.0); // tek þetta ut bara svo geri buildað
    }
    public void removeP(Patient p)
    {
        dataDeild.inni--;
        dataDeild.fjoldiInni[p.Aldur]--;
        if (p.Deild != simAttribs.states[5])
        {

        }
    }
}

