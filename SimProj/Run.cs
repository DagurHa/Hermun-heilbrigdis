using System.Diagnostics;
using Newtonsoft.Json.Linq;
namespace SimProj;
//Console.OutputEncoding = System.Text.Encoding.UTF8;
public class Run
{
    public static bool upphitunFlag = false;

    public static void Main(string[] args)
    {
        Console.WriteLine("Hundur");
        string simString = args[0];
        JObject data = JObject.Parse(simString);
        Console.WriteLine(data["meðalfjöldi"].ToDictionary());
    }
}