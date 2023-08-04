/* 
 * Þessi class hermir deildir kerfisins  
 */
using SimSharp;

namespace SimProj;
public class Deild
{
    private Kerfi kerfi;
    public DeildInfo dataDeild;
    public SimAttribs simAttribs;
    private string nafn;
    private Simulation env;
    private Dictionary<string,MathNet.Numerics.Distributions.LogNormal> waitLognorm = new Dictionary<string, MathNet.Numerics.Distributions.LogNormal>();
    private MathNet.Numerics.Distributions.ContinuousUniform WaitUnif;
    private double wait;
    public Deild(Simulation envment, string Nafn, SimAttribs SimAttributes, Kerfi Kerfi)
    {
        kerfi = Kerfi;
        env = envment;
        nafn = Nafn;
        simAttribs = SimAttributes;
        wait = 0;
        dataDeild = new DeildInfo(simAttribs);
        if(simAttribs.WaitLognorm.ContainsKey(nafn)){
            foreach (string age_grp in simAttribs.AgeGroups)
            {
                MathNet.Numerics.Distributions.LogNormal lgnrm = new MathNet.Numerics.Distributions.LogNormal(simAttribs.WaitLognorm[nafn][age_grp][0], simAttribs.WaitLognorm[nafn][age_grp][1]);
                waitLognorm[age_grp] = lgnrm;
            }
        }
        if (simAttribs.WaitUniform.ContainsKey(nafn))
        {
            WaitUnif = new MathNet.Numerics.Distributions.ContinuousUniform(simAttribs.WaitUniform[nafn][0], simAttribs.WaitUniform[nafn][1]);
        }
    }
    public IEnumerable<Event> addP(Patient p, bool innrit, string prev_deild)
    {
        if (innrit)
        {
            kerfi.deildir[prev_deild].dataDeild.fjoldiInni[p.Aldur]--;
            kerfi.deildir[prev_deild].dataDeild.inni--;
        }
        else
        {
            kerfi.telja++;
            kerfi.amount++;
        }
        dataDeild.fjoldiInni[p.Aldur]++;
        dataDeild.inni++;
        if (Run.upphitunFlag){dataDeild.fjoldiDag[p.Aldur][kerfi.Dagur]++; }
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
        if (prev == simAttribs.States[2] & newDeild == simAttribs.States[0]) { env.TimeoutD(0.9); }
        if (Run.upphitunFlag) { dataDeild.deildSkipt[newDeild]++; }
        if (simAttribs.FinalState.Contains(newDeild)) { removeP(p); }
        else
        {
            yield return env.Process(kerfi.deildir[newDeild].addP(p,true,prev));
        }
    }
    public void removeP(Patient p)
    {
        dataDeild.inni--;
        dataDeild.fjoldiInni[p.Aldur]--;
    }
}

