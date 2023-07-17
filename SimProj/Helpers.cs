using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SimProj;

public class Helpers
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
        for(int i = 0; i < deildir.Count; i++)
        {
            if (deildir[i] == deild) return i;
        }
        return -1;
    }
    /*Reiknum starfsþörf út frá hámarki sjúklinga sem komu í kerfið fyrir hverja deild
     Input: Listi af ints og SimAttribs struct
     */
    public Dictionary<(string,string),int> CalcNumJobs(List<int> maxIn,SimAttribs simAttribs)
    {
        IEnumerable<string> deildir = simAttribs.initState.Concat(simAttribs.medState);
        foreach(string state in deildir)
        {
            foreach(string job in simAttribs.jobs)
            {
                int nr = getDeildnr(state, simAttribs.states);
                int load = (int) maxIn[nr] / simAttribs.jobDdemand[(state, job)].Item1;
                starfs[(state, job)] = load * simAttribs.jobDdemand[(state, job)].Item2;
            }
        }
        return starfs;
    }
}
