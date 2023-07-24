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
    /*Reiknum starfsþörf út frá hámarki sjúklinga sem komu í kerfið fyrir hverja deild
     Input: Listi af ints og SimAttribs struct
     */
    public static Dictionary<(string, string), int> CalcNumJobs(int[] maxIn, SimAttribs simAttribs)
    {
        starfs = new Dictionary<(string, string), int>();
        IEnumerable<string> deildir = simAttribs.InitState.Concat(simAttribs.MedState);
        foreach (string state in deildir)
        {
            foreach (string job in simAttribs.Jobs)
            {
                int nr = getDeildnr(state, simAttribs.States);
                int load = maxIn[nr] / simAttribs.JobDemand[(state, job)][0];
                starfs.Add((state, job), load * simAttribs.JobDemand[(state, job)][1]);
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
}
