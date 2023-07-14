using System.Diagnostics;

namespace SimProj;

public class Run
{
    private static Random rnd = new Random();

    public static void Main(string[] args)
    {
        Console.WriteLine("Hello");
        List<double> test_p = new List<double>() { 0.1,0.4,0.3,0.2};
        Console.WriteLine(randomChoice(test_p));
    }
    public static int randomChoice(List<double> p)
    {
        double r = rnd.NextDouble();
        foreach(var item in p.Select((Value,Index) => new { Value, Index }))
        {
            r -= item.Value;
            if(r < 0)
            {
                return item.Index;
            }
        }
        return p.Count - 1;
    } 
}