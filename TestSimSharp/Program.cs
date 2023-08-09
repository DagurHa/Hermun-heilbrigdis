namespace Test;

using MathNet.Numerics;
using MathNet.Numerics.Distributions;
using System.ComponentModel;
using System.Linq;
using System.Windows.Markup;

public class Hundur
{
    public static void Main(string[] args)
    {
        LogNormal logNorm = new LogNormal(0.9163,0.8444);
        int N = 500;
        double[] vals = new double[N];
        for (int i = 0; i < N; i++)
        {
            vals[i] = logNorm.Sample().Round(4);
            Console.WriteLine(vals[i]);
        }
    }
}