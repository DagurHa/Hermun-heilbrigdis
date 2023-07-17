namespace SimProj;

public struct SimAttribs
{
    public Dictionary<string, int> meanArrive;
    public Dictionary<(string, string), List<double>> moveProb;
    public List<double> initialProb;
    public List<string> states;
    public List<string> age_grps;
    public Dictionary<string, Dictionary<string, (double, double)>> waitLognorm;
    public Dictionary<string, (double, double)> waitUniform;
    public int simAmount;
    public Dictionary<(string, string), int> deildaskipti; //Kannski ekki hafa þetta hér?
    public List<string> initState;
    public List<string> medState;
    public List<string> finalState;
    public int warmupTime;
    //private readonly Dictionary<string,float> endurkoma (þetta er useless einmitt nuna)
    public Dictionary<(string, string), (int,int)> jobDdemand; // Lykill er staða og starf og value er sjúklingar og fjöldi starfsmanna
    public List<(string, string)> keys;
    public List<string> jobs;
    public Dictionary<string, double> meanExp;
    public int lam;
    public bool showSim;
    public int stop;
}