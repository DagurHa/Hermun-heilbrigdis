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
        Simulation env = new Simulation();
        Kerfi kerfi = new Kerfi(env, simAttr);
        DataFinal data = new DataFinal(simAttr.Keys);
        env.Process(kerfi.interrupter(data));
        env.RunD((double?)(simAttr.Stop + simAttr.WarmupTime));
        Helpers.CalcData(simAttr, kerfi, data);
        data.Log();
    }
}