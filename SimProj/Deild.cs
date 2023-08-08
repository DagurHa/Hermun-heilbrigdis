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
    }
    public IEnumerable<Event> addP(Patient p, bool innrit, string prev_deild)
    {
        if (innrit)
        {
            kerfi.deildir[prev_deild].dataDeild.fjoldiInni[p.Aldur]--;
            kerfi.deildir[prev_deild].dataDeild.inni--;
        }
        else { kerfi.amount++; }
        dataDeild.fjoldiInni[p.Aldur]++;
        dataDeild.inni++;
        if (Run.upphitunFlag && !simAttribs.PeriodStates.Contains(nafn))
        { 
            dataDeild.fjoldiDag[p.Aldur][kerfi.Dagur]++;
            kerfi.telja++;
        }
        if (dataDeild.inni > dataDeild.maxInni){ dataDeild.maxInni = dataDeild.inni; }
        if (simAttribs.WaitLognorm.ContainsKey(nafn))
        {
            wait = waitLognorm[p.Aldur].Sample();
            yield return env.TimeoutD(wait);
        }
        if (simAttribs.PeriodStates.Contains(nafn))
        {
            yield return env.TimeoutD(30.0);
            int inxNextDeild = Helpers.randomChoice(simAttribs.MoveProb[(nafn, p.Aldur)]);
            string NextDeild = simAttribs.States[inxNextDeild];
            if (NextDeild == simAttribs.States[0])
            {
                p.Deild = NextDeild;
                if (Run.upphitunFlag) { dataDeild.deildSkipt[NextDeild]++; }
                yield return env.Process(kerfi.deildir[NextDeild].addP(p, true, nafn));
            }
            else
            {
                double wait = simAttribs.PeriodDays[(p.Aldur, nafn)] / simAttribs.PeriodStays[(p.Aldur, nafn)];
                yield return env.Process(TreatmentPeriod(p, simAttribs.PeriodDays[(p.Aldur, nafn)], wait));
            }
        }
        else { yield return env.Process(updatePatient(p)); }
    }
    public IEnumerable<Event> updatePatient(Patient p)
    {
        int i_deild = Helpers.randomChoice(simAttribs.MoveProb[(nafn,p.Aldur)]);
        string newDeild = simAttribs.States[i_deild];
        string prev = p.Deild;
        p.Deild = newDeild;
        if (prev == simAttribs.States[3] & newDeild == simAttribs.States[0]) { env.TimeoutD(0.9); }
        if (Run.upphitunFlag) { dataDeild.deildSkipt[newDeild]++; }
        if (simAttribs.FinalState.Contains(newDeild)) { removeP(p); }
        else
        {
            yield return env.Process(kerfi.deildir[newDeild].addP(p,true,prev));
        }
    }
    public IEnumerable<Event> TreatmentPeriod(Patient p, double KomurLeft, double wait)
    {
        while(KomurLeft >= 0.0)
        {
            yield return env.TimeoutD(wait);
            dataDeild.fjoldiDag[p.Aldur][kerfi.Dagur]++;
            KomurLeft -= 1.0;
        }
        //Einu deildirnar sem sjúklingur getur farið á eftir meðferðarlotu eru "heim" og "legudeild"
        if (Run.upphitunFlag) { dataDeild.deildSkipt["heim"]++; }
        removeP(p);
    }
    public void removeP(Patient p)
    {
        dataDeild.inni--;
        dataDeild.fjoldiInni[p.Aldur]--;
    }
}

