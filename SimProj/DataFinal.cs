using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SimProj;

public class DataFinal
{
    public Dictionary<string, List<int>> fjoldiDag = new Dictionary<string, List<int>>();
    public Dictionary<string, int> maxInni = new Dictionary<string, int>();
    public Dictionary<(string, string), List<int>> deildAgeAmount = new Dictionary<(string, string), List<int>>();

    public void Log()
    {
        foreach(string key in maxInni.Keys)
        {
            Console.WriteLine($"Deild: {key} og max inni {maxInni[key]}");
        }
    }
}
