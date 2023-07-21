/*
    Hér geymum við struct sem heldur utan um gögn sérhverrar deildar.
 */

namespace SimProj;

public class DeildInfo
{
    public List<int> fjoldiDag = new List<int>(); //Fjöldi sjúklinga sem koma inn yfir daginn
    public int maxInni = 0;          //Hámarksfjöldi sjúklinga sem voru inni yfir hermunina
    public Dictionary<string,int> fjoldiInni = new Dictionary<string, int>();//Fjöldi sjúklinga inni á enda dags
    public int inni = 0;
    public int[] deildSkipt; // Deildarskipti fyrir deildina sem þetta struct sér um
    public DeildInfo(SimAttribs simAttribs)
    {
        foreach(string age_grp in simAttribs.AgeGroups) { fjoldiInni[age_grp] = 0; }
        int arrLen = simAttribs.States.Count;
        deildSkipt = new int[arrLen];
        foreach(string key in simAttribs.States) { Console.WriteLine($"STATE: {key}"); }
        for(int i = 0; i < arrLen; i++) { deildSkipt[i] = 0; }
    }
}