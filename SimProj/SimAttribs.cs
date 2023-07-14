namespace SimProj;

public struct SimAttribs
{
    public Dictionary<string, int> meanArrive = new Dictionary<string, int>();
    public Dictionary<(string, string), List<double>> moveProb = new Dictionary<(string, string), List<double>>();
    public List<double> initialProb = new List<double>();
    public List<string> states = new List<string>();
    public List<string> age_grps = new List<string>();
    public Dictionary<string, Dictionary<string, (double, double)>> waitLognorm = new Dictionary<string, Dictionary<string, (double, double)>>();
    public Dictionary<string, (double, double)> waitUniform = new Dictionary<string, (double, double)>();
    public int simAmount;
    public Dictionary<(string, string), int> deildaskipti = new Dictionary<(string, string), int>(); //Kannski ekki hafa þetta hér?
    public List<string> initState = new List<string>();
    public List<string> medState = new List<string>();
    public List<string> finalState = new List<string>();
    public int warmupTime;
    //private readonly Dictionary<string,float> endurkoma (þetta er useless einmitt nuna)
    public Dictionary<(string, string), List<int>> jobDdemand = new Dictionary<(string, string), List<int>>();
    public List<(string, string)> keys = new List<(string, string)>();
    public List<string> jobs = new List<string>();
    public Dictionary<string, double> meanExp = new Dictionary<string, double>();
    public int lam;

    public SimAttribs()
    {
    }
}