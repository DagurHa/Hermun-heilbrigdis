using System.Diagnostics;

namespace SimProj;

public class Run
{
    public static bool upphitunFlag = false;

    public static void Main(string[] args)
    {
        Console.WriteLine("Hello");
        List<double> test_p = new List<double>() { 0.1,0.4,0.3,0.2};
        Console.WriteLine(Helpers.randomChoice(test_p));
    } 
}