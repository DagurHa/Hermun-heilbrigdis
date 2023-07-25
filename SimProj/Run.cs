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
    public static Kerfi? kerfi;
    public static bool upphitunFlag = false;
    public const string pth = @"./SimProj/Test.txt";
    public static void Main(string[] args)
    {
        File.WriteAllText(pth, string.Empty);
        string simString_nontup = args[0];
        string simString_tup = args[1];
        Debug.Assert(simString_nontup is not null && simString_tup is not null);
        SimAttribsNontuples? simAttrNontup = JsonConvert.DeserializeObject<SimAttribsNontuples>(simString_nontup);
        SimAttribsTuples? simAttrTup = JsonConvert.DeserializeObject<SimAttribsTuples>(simString_tup);
        SimAttribs simAttr = new SimAttribs();
        simAttr.initNonTuple(simAttrNontup);
        simAttr.initTuple(simAttrTup);
        Simulation env = new Simulation();
        DataFinal data = new DataFinal(simAttr.Keys);
        kerfi = new Kerfi(env, simAttr);
        env.Process(kerfi.interrupter(data));
        env.RunD((double?)(simAttr.Stop + simAttr.WarmupTime));
        int[] maxIn = new int[simAttr.States.Count];
        foreach (string state in simAttr.States)
        {
            data.maxInni.Add(state, kerfi.data[state].maxInni);
            maxIn[Helpers.getDeildnr(state, simAttr.States)] = data.maxInni[state];
        }
        data.HeildarPatient = kerfi.telja;
        data.JobNum = Helpers.CalcNumJobs(maxIn, simAttr);
        data.Log();
    }
}