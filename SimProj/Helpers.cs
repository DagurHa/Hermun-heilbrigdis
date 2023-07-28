using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Globalization;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

namespace SimProj;

public static class Helpers
{
    private static Dictionary<(string,string), int> starfs;
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
        return p.Count - 1;
    }
    public static int getDeildnr(string deild, List<string> deildir)
    {
        for (int i = 0; i < deildir.Count; i++)
        {
            if (deildir[i] == deild) return i;
        }
        return -1;
    }
    /*
     Reiknum starfsþörf út frá hámarki sjúklinga sem komu í kerfið fyrir hverja deild
     Input: Listi af ints og SimAttribs struct
     */
    public static Dictionary<(string,string), int> CalcNumJobs(int[] maxIn, SimAttribs simAttribs)
    {
        starfs = new Dictionary<(string,string), int>();
        IEnumerable<string> deildir = simAttribs.InitState.Concat(simAttribs.MedState);
        foreach (string state in deildir)
        {
            foreach (string job in simAttribs.Jobs)
            {
                int nr = getDeildnr(state, simAttribs.States);
                double load = Math.Ceiling((double)maxIn[nr] / simAttribs.JobDemand[(state, job)][0]);
                starfs.Add((state,job), (int)load * simAttribs.JobDemand[(state, job)][1]);
            }
        }
        return starfs;
    }
    public static (string,string) StringToTup(string ogString)
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
        int[] maxIn = new int[simAttr.States.Count];
        foreach (string state in simAttr.States)
        {
            data.maxInni.Add(state, kerfi.data[state].maxInni);
            if (!simAttr.FinalState.Contains(state)) { maxIn[getDeildnr(state, simAttr.States)] = data.maxInni[state]; }
        }
        data.HeildarPatient = kerfi.telja;
        data.JobNum = CalcNumJobs(maxIn, simAttr);
        foreach(string state in kerfi.deildir.Keys)
        {
            data.fjoldiDag.Add(state, kerfi.deildir[state].dataDeild.fjoldiDag);
        }
        foreach((string,string) key in simAttr.DeildaSkipti.Keys)
        {
            string[] sankKey = { key.Item1, key.Item2 };
            if (kerfi.deildir.ContainsKey(key.Item1)){
                data.SankeyData.Add(sankKey, kerfi.deildir[key.Item1].dataDeild.deildSkipt[getDeildnr(key.Item2, simAttr.States)]);
            }
        }
    }
}
