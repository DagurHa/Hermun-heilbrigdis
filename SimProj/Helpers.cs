using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SimProj;

public class Helpers
{
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
}
