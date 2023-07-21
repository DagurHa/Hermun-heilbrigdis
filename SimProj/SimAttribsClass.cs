using Newtonsoft.Json;
using Newtonsoft.Json.Bson;
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
    public Dictionary<string,double>? MeanExp {  get; set; }
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

    /*
     Geyma
     Type nonTupType = typeof(SimAttribsTuples);

        // Get all the properties of the parent class
        PropertyInfo[] nonTupProperties = nonTupType.GetProperties(BindingFlags.Public | BindingFlags.Instance);

        // Iterate over the properties and set the corresponding properties of the child class
        foreach (var property in nonTupProperties)
        {
            if (property.PropertyType.IsGenericType &&
                property.PropertyType.GetGenericTypeDefinition() == typeof(Dictionary<,>) &&
                property.PropertyType.GetGenericArguments()[0] == typeof(string))
            {
                var PropDict = property.GetValue(simAttr);
                if (property.CanRead && property.CanWrite)
                {
                    Dictionary<(string, string), object> TupDict = new Dictionary<(string, string), object>();
                    foreach(string key in PropDict.Keys)
                    {
                        (string,string) keyTup = Helpers.StringToTup(key);
                        TupDict[keyTup] = PropDict[key];
                    }
                    property.SetValue(this, TupDict);        // Set the value in the current instance (child object)
                }
            }
        }
     */
    public void initTuple(SimAttribsTuples simAttr)
    {
        //Höfum basic til að byrja með
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
        Type type = typeof(SimAttribs);

        // Get all the properties of the parent class
        PropertyInfo[] Props = type.GetProperties(BindingFlags.Public | BindingFlags.Instance);

        // Iterate over the properties and set the corresponding properties of the child class
        foreach (var prop in Props)
        {
            var value = prop.GetValue(this);
            Console.WriteLine($"Prop : {prop.Name} með val : {value}");
        }
    }
}

public class SimAttribsTuples
{
    //Allir lyklar hér eiga að vera (string,string) en eru string til að byrja með
    public Dictionary<string, List<double>>? MoveProb { get; set; }
    public Dictionary<string, int>? DeildaSkipti { get; set; }
    public Dictionary<string, List<int>>? JobDemand { get; set; }

}