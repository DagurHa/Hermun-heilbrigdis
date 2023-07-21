using System.Diagnostics;
using Newtonsoft.Json.Linq;
using Newtonsoft.Json;
using SimSharp;

namespace SimProj;
//Console.OutputEncoding = System.Text.Encoding.UTF8;
public class Run
{
    public static bool upphitunFlag = false;

    public static void Main(string[] args)
    {
        Console.WriteLine("Hundur");
        string simString_nontup = args[0];
        string simString_tup = args[1];
        Debug.Assert(simString_nontup is not null && simString_tup is not null);
        SimAttribsNontuples simAttrNontup = JsonConvert.DeserializeObject<SimAttribsNontuples>(simString_nontup);
        SimAttribsTuples simAttrTup = JsonConvert.DeserializeObject<SimAttribsTuples>(simString_tup);
        SimAttribs simAttr = new SimAttribs();
        simAttr.initNonTuple(simAttrNontup);
        simAttr.initTuple(simAttrTup);
        simAttr.Log();
        Simulation env = new Simulation();
        DataFinal data = new DataFinal();
        Kerfi kerfi = new Kerfi(env, simAttr);
        env.Process(kerfi.interrupter(data));
        Console.WriteLine($"Simtime : {simAttr.Stop} og upphitun : {simAttr.WarmupTime}");
        //env.RunD((double?)(simAttr.Stop + simAttr.WarmupTime));
        data.Log();
        }
    }