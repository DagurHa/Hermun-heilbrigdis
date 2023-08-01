using System.Reflection;

namespace SimProj;

public class SimAttribsNontuples
{
    public Dictionary<string,int>? MeanArrive { get; set; }
    public List<double>? InitialProb { get; set; }
    public List<string>? States { get; set; }
    public List<string>? AgeGroups { get; set; }
    public Dictionary<string, Dictionary<string,List<double>>>? WaitLognorm {  get; set; }
    public Dictionary<string,List<double>>? WaitUniform { get; set; }
    public int SimAmount { get; set; }
    public List<string>? InitState { get; set; }
    public List<string>? MedState { get; set; }
    public List<string>? FinalState { get; set; }
    public int WarmupTime { get; set; }
    public Dictionary<string,double>? ReEnter { get; set; }
    public List<List<string>>? Keys { get; set; }
    public List<string>? Jobs { get; set; }
    public Dictionary<string,double>? MeanWait {  get; set; }
    public double Lam { get; set; }
    public bool ShowSim { get; set; }
    public int Stop { get; set; }
}
public class SimAttribs : SimAttribsNontuples
{
    public Dictionary<(string, string), List<double>>? MoveProb { get; set; }
    public Dictionary<(string, string), int>? DeildaSkipti { get; set; }
    public Dictionary<(string, string), List<int>>? JobDemand { get; set; }

    public void initNonTuple(SimAttribsNontuples simAttr)
    {
        Type parentType = typeof(SimAttribsNontuples);

        // Get all the properties of the parent class
        PropertyInfo[] parentProperties = parentType.GetProperties(BindingFlags.Public | BindingFlags.Instance);

        // Iterate over the properties and set the corresponding properties of the child class
        foreach (var property in parentProperties)
        {
            if (property.CanRead && property.CanWrite)
            {
                var value = property.GetValue(simAttr); // Get the value from the parent object
                property.SetValue(this, value);        // Set the value in the current instance (child object)
            }
        }
    }

    public void initTuple(SimAttribsTuples simAttr)
    {
        MoveProb = new Dictionary<(string, string), List<double>>();
        JobDemand = new Dictionary<(string, string), List<int>>();
        DeildaSkipti = new Dictionary<(string, string), int>();
        foreach(var key in simAttr.MoveProb.Keys)
        {
            (string, string) keyTup = Helpers.StringToTup(key);
            MoveProb[keyTup] = simAttr.MoveProb[key];
        }
        foreach (var key in simAttr.JobDemand.Keys)
        {
            (string, string) keyTup = Helpers.StringToTup(key);
            JobDemand[keyTup] = simAttr.JobDemand[key];
        }
        foreach (var key in simAttr.DeildaSkipti.Keys)
        {
            (string, string) keyTup = Helpers.StringToTup(key);
            DeildaSkipti[keyTup] = simAttr.DeildaSkipti[key];
        }
    }
    public void Log()
    {
        Console.WriteLine("MoveProb:");
        foreach((string,string) key in MoveProb.Keys)
        {
            Console.WriteLine($"Lykill: {key}");
            foreach(double item in MoveProb[key])
            {
                Console.WriteLine($"Item: {item}");
            }
        }
        Console.WriteLine("Deildaskipti:");
        foreach ((string, string) key in DeildaSkipti.Keys)
        {
            Console.WriteLine($"Lykill: {key} og value {DeildaSkipti[key]}");
        }
        Console.WriteLine("JobDemand:");
        foreach((string,string) key in JobDemand.Keys)
        {
            Console.WriteLine($"Lykill: {key}");
            foreach(int item in JobDemand[key])
            {
                Console.WriteLine($"Item: {item}");
            }
        }
        Console.WriteLine("MeanArrive:");
        foreach(string key in MeanArrive.Keys)
        {
            Console.WriteLine($"Lykill: {key} Item: {MeanArrive[key]}");
        }
        Console.WriteLine("InitialProb:");
        foreach(double item in InitialProb)
        {
            Console.WriteLine($"Item: {item}");
        }
        Console.WriteLine("States:");
        foreach(string item in States)
        {
            Console.WriteLine($"Item: {item}");
        }
        Console.WriteLine("AgeGroups:");
        foreach(string item in AgeGroups)
        {
            Console.WriteLine($"Item: {item}");
        }
        Console.WriteLine("WaitLognorm:");
        foreach(string key1 in WaitLognorm.Keys)
        {
            Console.WriteLine($"Lykill 1 : {key1}");
            foreach(string key2 in WaitLognorm[key1].Keys)
            {
                Console.WriteLine($"Lykill 2: {key2}");
                foreach(double item in WaitLognorm[key1][key2])
                {
                    Console.WriteLine($"Item: {item}");
                }
            }
        }
        Console.WriteLine("WaitUniform:");
        foreach(string key in WaitUniform.Keys)
        {
            Console.WriteLine($"Lykill: {key}");
            foreach(double item in WaitUniform[key])
            {
                Console.WriteLine($"Item : {item}");
            }
        }
        Console.WriteLine($"SimAmount: {SimAmount}");
        Console.WriteLine("InitState:");
        foreach(string item in InitState)
        {
            Console.WriteLine($"Item: {item}");
        }
        Console.WriteLine("MedState:");
        foreach(string item in MedState)
        {
            Console.WriteLine($"Item: {item}");
        }
        Console.WriteLine("FinalState:");
        foreach(string item in FinalState)
        {
            Console.WriteLine($"Item: {item}");
        }
        Console.WriteLine($"WarmupTime: {WarmupTime}");
        Console.WriteLine("ReEnter:");
        foreach(string key in ReEnter.Keys)
        {
            Console.WriteLine($"Lykill: {key} og Item: {ReEnter[key]}");
        }
        Console.WriteLine("Keys:");
        foreach(List<string> lstKey in Keys)
        {
            Console.WriteLine("Listi:");
            foreach(string item in lstKey)
            {
                Console.WriteLine($"Item: {item}");
            }
        }
        Console.WriteLine("Jobs:");
        foreach(string item in Jobs)
        {
            Console.WriteLine($"Item: {item}");
        }
        Console.WriteLine("MeanWait:");
        foreach(string key in MeanWait.Keys)
        {
            Console.WriteLine($"Lykill: {key} og Item: {MeanWait[key]}");
        }
        Console.WriteLine($"Lam: {Lam}");
        Console.WriteLine($"ShowSim: {ShowSim}");
        Console.WriteLine($"Stop: {Stop}");
    }
}

public class SimAttribsTuples
{
    //Allir lyklar hér eiga að vera (string,string) en eru string til að byrja með
    public Dictionary<string, List<double>>? MoveProb { get; set; }
    public Dictionary<string, int>? DeildaSkipti { get; set; }
    public Dictionary<string, List<int>>? JobDemand { get; set; }

}