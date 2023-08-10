/*
    Hér er Class sem heldur utan um gögn sérhverrar deildar.
 */

namespace SimProj;

public class DeildInfo
{
    public Dictionary<string,double> totalTime; //Heildartími sjúklinga eftir aldurshópi á þessari deild
    public Dictionary<string, int[]> fjoldiDag; //Fjöldi sjúklinga sem koma á deildina yfir daginn (þurfa ekki að vera unique)
    public int maxInni = 0;          //Hámarksfjöldi sjúklinga sem voru inni á deildinni yfir hermunina
    public Dictionary<string,int> fjoldiInni = new Dictionary<string, int>();//Fjöldi sjúklinga inni á enda dags eftir aldri
    public int inni = 0; //Fjöldi inni á deildinni í heild
    public Dictionary<string,int> deildSkipt; // Deildarskipti fyrir deildina sem þessi class sér um
    public DeildInfo(SimAttribs simAttribs)
    {
        totalTime = new Dictionary<string, double>();
        fjoldiDag = new Dictionary<string, int[]>();
        foreach(string age_grp in simAttribs.AgeGroups)
        { 
            fjoldiInni[age_grp] = 0;
            fjoldiDag.Add(age_grp, new int[simAttribs.Stop + simAttribs.WarmupTime]);
            totalTime[age_grp] = 0.0;
        }
        deildSkipt = new Dictionary<string, int>();
        foreach(string state in simAttribs.States) { deildSkipt.Add(state, 0); }
    }
}