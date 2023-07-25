/*
    Hér geymum við struct sem heldur utan um gögn sérhverrar deildar.
 */

namespace SimProj;

public class DeildInfo
{
    public int[] fjoldiDag; //Fjöldi sjúklinga sem koma á deildina yfir daginn (þurfa ekki að vera unique)
    public int maxInni = 0;          //Hámarksfjöldi sjúklinga sem voru inni á deildinni yfir hermunina
    public Dictionary<string,int> fjoldiInni = new Dictionary<string, int>();//Fjöldi sjúklinga inni á enda dags
    public int inni = 0;
    public int[] deildSkipt; // Deildarskipti fyrir deildina sem þessi class sér um
    public DeildInfo(SimAttribs simAttribs)
    {
        foreach(string age_grp in simAttribs.AgeGroups) { fjoldiInni[age_grp] = 0; }
        fjoldiDag = new int[simAttribs.Stop + simAttribs.WarmupTime];
        int arrLen = simAttribs.States.Count;
        deildSkipt = new int[arrLen];
        for(int i = 0; i < arrLen; i++) { deildSkipt[i] = 0; }
    }
}