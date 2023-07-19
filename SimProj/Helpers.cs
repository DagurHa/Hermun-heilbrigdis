using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Globalization;
using System.Linq;
using System.Reflection;
using System.Text;
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
    public static Dictionary<(string, string), int> CalcNumJobs(List<int> maxIn, SimAttribs simAttribs)
    {
        IEnumerable<string> deildir = simAttribs.InitState.Concat(simAttribs.MedState);
        foreach (string state in deildir)
        {
            foreach (string job in simAttribs.Jobs)
            {
                int nr = getDeildnr(state, simAttribs.States);
                int load = maxIn[nr] / simAttribs.JobDemand[(state, job)].Item1;
                starfs[(state, job)] = load * simAttribs.JobDemand[(state, job)].Item2;
            }
        }
        return starfs;
    }
    public static SimAttribs initSimattribs(JObject data)
    {
        //TypeDescriptor.AddAttributes(typeof((string, string)), new TypeConverterAttribute(typeof(TupleConverter<string, string>)));

        SimAttribs simAttribs = new SimAttribs();
        foreach (PropertyInfo prop in typeof(SimAttribs).GetProperties())
        {
            Console.WriteLine($"Key er {prop.Name} og value er {data[prop.Name]} og value type er {prop.PropertyType}");
            //prop.SetValue(simAttribs, data[prop.Name].ToObject(prop.PropertyType));
        }
        return simAttribs;
    }
}
