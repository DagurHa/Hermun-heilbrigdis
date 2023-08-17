using Newtonsoft.Json;
using System.Linq;
using System.Text.RegularExpressions;

namespace SimProj;

public static class Helpers
{
    private static Dictionary<(string, string), int> starfs;
    private static Random rnd = new Random();
    public static int randomChoice(List<double> p)
    {
        double r = rnd.NextDouble();
        foreach (var item in p.Select((Value, Index) => new { Value, Index }))
        {
            r -= item.Value;
            if (r < 0)
            {
                return item.Index;
            }
        }
        throw new Exception("Færslulíkur summast ekki í 1");
    }
    /*
     Reiknum starfsþörf út frá hámarki sjúklinga sem komu í kerfið fyrir hverja deild
     Input: Listi af ints og SimAttribs struct
     */
    public static Dictionary<(string, string), int> CalcNumJobs(Dictionary<string, int> maxIn, SimAttribs simAttribs)
    {
        starfs = new Dictionary<(string, string), int>();
        List<string> deildir = new List<string> { "legudeild", "bráðamóttaka", "heilsugæsla" };
        foreach (string state in deildir)
        {
            foreach (string job in simAttribs.Jobs)
            {
                double load = Math.Ceiling((double)maxIn[state] / simAttribs.JobDemand[(state, job)][0]);
                starfs.Add((state, job), (int)load * simAttribs.JobDemand[(state, job)][1]);
            }
        }
        return starfs;
    }
    public static (string, string) StringToTup(string ogString)
    {
        string pattern = @"\('([^']*)', '([^']*)'\)";
        Match match = Regex.Match(ogString, pattern);

        if (match.Success)
        {
            string string1 = match.Groups[1].Value;
            string string2 = match.Groups[2].Value;
            return (string1, string2);
        }
        else
        {
            throw new ArgumentException("Input string format is not valid.");
        }
    }
    public static SimAttribs InitSimAttr(string JsonTuple, string JsonNonTuple)
    {
        SimAttribsNontuples? simAttrNontup = JsonConvert.DeserializeObject<SimAttribsNontuples>(JsonNonTuple);
        SimAttribsTuples? simAttrTup = JsonConvert.DeserializeObject<SimAttribsTuples>(JsonTuple);
        SimAttribs simAttr = new SimAttribs();
        simAttr.initNonTuple(simAttrNontup);
        simAttr.initTuple(simAttrTup);
        return simAttr;
    }
    public static void CalcData(SimAttribs simAttr, Kerfi kerfi, DataFinal data)
    {
        Dictionary<string, int> maxIn = new Dictionary<string, int>();
        foreach (string state in kerfi.deildir.Keys)
        {
            data.maxInni.Add(state, kerfi.deildir[state].dataDeild.maxInni);
            if (!simAttr.FinalState.Contains(state)) { maxIn.Add(state, data.maxInni[state]); }
        }
        data.HeildarPatient = kerfi.telja;
        data.JobNum = CalcNumJobs(maxIn, simAttr);
        foreach (List<string> key in simAttr.Keys)
        {
            (string, string) keyTup = (key[0], key[1]);
            data.fjoldiDag.Add(keyTup, kerfi.deildir[key[1]].dataDeild.fjoldiDag[key[0]]);
        }
        foreach ((string, string) key in simAttr.DeildaSkipti.Keys)
        {
            if (kerfi.deildir.ContainsKey(key.Item1))
            {
                data.SankeyData.Add(key, kerfi.deildir[key.Item1].dataDeild.deildSkipt[key.Item2]);
            }
        }
        foreach (string deild in simAttr.MedState)
        {
            foreach (string age in simAttr.AgeGroups)
            {
                int totalPatientAge = kerfi.deildir[deild].dataDeild.AgeGrad[age];
                data.meanTime[(age,deild)] = (double) kerfi.deildir[deild].dataDeild.totalTime[age]/totalPatientAge;
            }
        }
    }
}
