using System.Diagnostics;
using Newtonsoft.Json.Linq;
using Newtonsoft.Json;
using SimSharp;
using System.IO.Enumeration;
using System.IO;

namespace SimProj;
//Console.OutputEncoding = System.Text.Encoding.UTF8;
public class Run
{
    public static bool upphitunFlag = false;
    public const string pth = @"./SimProj/Test.txt";
    public static void Main(string[] args)
    {
        //Gera file empty fyrir næstu hermun
        File.WriteAllText(pth, string.Empty);
        string simString_nontup = args[0];
        string simString_tup = args[1];
        SimAttribs simAttr = Helpers.InitSimAttr(simString_tup, simString_nontup);
        TotalData retData = hermHundur(simAttr);
        var jsonRetString = JsonConvert.SerializeObject(retData,Formatting.Indented);
        string jsonPth = "JSONOUTPUT.json";
        File.WriteAllText(jsonPth, jsonRetString);
    }
    //Fall sem hermir kerfið einu sinni með völdum stillingum.
    private static DataFinal sim(SimAttribs simAttr)
    {
        DataFinal data = new DataFinal(simAttr.Keys);
        Simulation env = new Simulation();
        Kerfi kerfi = new Kerfi(env, simAttr);
        env.Process(kerfi.interrupter(data));
        env.RunD((double?)(simAttr.Stop + simAttr.WarmupTime));
        Helpers.CalcData(simAttr, kerfi, data);
        return data;
    }
    private static TotalData hermHundur(SimAttribs simAttr)
    {
        int L = simAttr.SimAmount;
        int days = simAttr.Stop - 1;
        List<List<int>> stayData = new List<List<int>>();
        TotalData totalData = new TotalData(simAttr);
        for(int i = 0; i < L; i++)
        {
            DataFinal data = sim(simAttr);
            stayData.Add(data.LeguAmount);
            foreach(string[] key in data.deildAgeAmount.Keys)
            {
                totalData.BoxPlot.Add(key, (double)data.deildAgeAmount[key].Sum()/days);
            }
            foreach ((string,string) JobKey in data.JobNum.Keys)
            {
                totalData.StarfsInfo[JobKey].Add(data.JobNum[JobKey]);
            }
            totalData.Sankey = data.SankeyData;
            totalData.totalPatient.Add(data.HeildarPatient);
        }
        foreach(List<int> legaHerm in stayData)
        {
            totalData.MeanLega.Add(legaHerm.Sum()/legaHerm.Count());
        }
        return totalData;
    }
}