namespace SimProj;

public class SimAttribs
{
    public Dictionary<string,int> MeanArrive { get; set; }
    public Dictionary<(string,string),List<double>> MoveProb {  get; set; }
    public List<double> InitialProb { get; set; }
    public List<string> States { get; set; }
    public List<string> AgeGroups { get; set; }
    public Dictionary<string, Dictionary<string,(double,double)>> WaitLognorm {  get; set; }
    public Dictionary<string,(double,double)> WaitUniform { get; set; }
    public int SimAmount { get; set; }
    public Dictionary<(string,string),int> DeildaSkipti { get; set; }
    public List<string> InitState { get; set; }
    public List<string> MedState { get; set; }
    public List<string> FinalState { get; set; }
    public int WarmupTime { get; set; }
    public Dictionary<string,double> ReEnter { get; set; }
    public Dictionary<(string, string), (int, int)> JobDemand { get; set; }
    public List<(string,string)> Keys { get; set; }
    public List<string> Jobs { get; set; }
    public Dictionary<string,double> MeanExp {  get; set; }
    public double Lam { get; set; }
    public bool ShowSim { get; set; }
    public int Stop { get; set; }
}