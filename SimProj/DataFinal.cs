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
    public Dictionary<(string, string), List<int>> deildAgeAmount;
    public List<int> LeguAmount;
    public int HeildarPatient;
    public Dictionary<(string, string), int> JobNum;

    public DataFinal(List<List<string>> keys)
    {
        deildAgeAmount = new Dictionary<(string, string), List<int>>();
        foreach(List<string> lst_key in keys)
        {
            deildAgeAmount.Add((lst_key[0], lst_key[1]), new List<int>());
        }
        LeguAmount = new List<int>();
    }

    public void Log()
    {
        File.AppendAllText(Run.pth, "Gögn um kerfið:" + Environment.NewLine);
        foreach(string key in maxInni.Keys)
        {
            File.AppendAllText(Run.pth,$"Lykill {key} og max inni eru {maxInni[key]}" + Environment.NewLine);
        }
        foreach((string,string) key in JobNum.Keys)
        {
            File.AppendAllText(Run.pth, $"Lykill {key} og starfsþörf: {JobNum[key]}" + Environment.NewLine);
        }
    }
}
