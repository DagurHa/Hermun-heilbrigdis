using Newtonsoft.Json;
using SimSharp;

namespace SimProj;
//Console.OutputEncoding = System.Text.Encoding.UTF8;
public class Run
{
    public static bool upphitunFlag = false;
    public static void Main(string[] args)
    {
        string pth = "./SimProj/bin/Release/net7.0/";
        string simString_tup = File.ReadAllText(pth+"InputTuple.json");
        string simString_nontup = File.ReadAllText(pth+"InputNonTuple.json");
        SimAttribs simAttr = Helpers.InitSimAttr(simString_tup, simString_nontup);
        TotalData retData = hermHundur(simAttr);
        var jsonRetString = JsonConvert.SerializeObject(retData,Formatting.Indented);
        string jsonPth = pth + "JSONOUTPUT.json";
        File.WriteAllText(jsonPth, jsonRetString);
    }
    //Fall sem hermir kerfið einu sinni með völdum stillingum.
    private static DataFinal sim(SimAttribs simAttr)
    {
        DataFinal data = new DataFinal(simAttr.Keys);
        Simulation env = new Simulation();
        Kerfi kerfi = new Kerfi(env, simAttr);
        env.Process(kerfi.interrupter(data));
        env.RunD(simAttr.Stop + simAttr.WarmupTime);
        Helpers.CalcData(simAttr, kerfi, data);
        return data;
    }
    
    private static TotalData hermHundur(SimAttribs simAttr)
    {
        int days = simAttr.Stop - 1;
        List<List<double>> stayData = new List<List<double>>();
        TotalData totalData = new TotalData(simAttr);
        Dictionary<(string, string), List<int>> SankeyData = new Dictionary<(string, string), List<int>>();
        foreach((string,string) key in simAttr.DeildaSkipti.Keys) { SankeyData.Add(key, new List<int>()); }
        for(int i = 0; i < simAttr.SimAmount; i++)
        {
            DataFinal data = sim(simAttr);
            upphitunFlag = false;
            stayData.Add(data.LeguAmount);
            foreach(string[] key in data.deildAgeAmount.Keys)
            {
                (string, string) keyTup = (key[0], key[1]);
                totalData.BoxPlot[keyTup].Add((double)data.deildAgeAmount[key].Sum()/days);
                for(int j = 0; j < simAttr.Stop; j++) { totalData.MeanAmount[keyTup][i, j] = data.fjoldiDag[keyTup][j]; }
            }
            foreach ((string,string) JobKey in data.JobNum.Keys)
            {
                totalData.StarfsInfo[JobKey].Add(data.JobNum[JobKey]);
            }
            foreach((string,string) SankeyKey in data.SankeyData.Keys)
            {
                SankeyData[SankeyKey].Add(data.SankeyData[SankeyKey]);
            }
            totalData.totalPatient.Add(data.HeildarPatient);
        }
        totalData.Sankey = SankeyData;
        foreach (List<double> legaHerm in stayData)
        {
            totalData.MeanLega.Add(legaHerm.Sum()/legaHerm.Count);
        }
        return totalData;
    }
}