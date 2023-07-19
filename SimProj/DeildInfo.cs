/*
    Hér geymum við struct sem heldur utan um gögn sérhverrar deildar.
 */

namespace SimProj;

public struct DeildInfo
{
    public List<int> fjoldiDag = new List<int>(); //Fjöldi sjúklinga sem koma inn yfir daginn
    public int maxInni = 0;          //Hámarksfjöldi sjúklinga sem voru inni yfir hermunina
    public Dictionary<string,int> fjoldiInni = new Dictionary<string, int>();//Fjöldi sjúklinga inni á enda dags
    public int inni = 0;
    public List<int> deildSkipt = new List<int>(); // Deildarskipti fyrir deildina sem þetta struct sér um
    public DeildInfo(SimAttribs simAttribs)
    {
        foreach(string age_grp in simAttribs.AgeGroups) { fjoldiInni[age_grp] = 0; }
        deildSkipt.Capacity = simAttribs.States.Count;
        for(int i = 0; i < deildSkipt.Capacity; i++) { deildSkipt[i] = 0; }
    }
}