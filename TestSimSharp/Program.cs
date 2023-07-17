using SimSharp;
using System;
using System.Runtime.CompilerServices;
using static SimSharp.Distributions;
using static System.Collections.Specialized.BitVector32;

class Sim {
    public TimeSpan SIMTIME = TimeSpan.FromHours(25);
    IDistribution<TimeSpan> dooexp = EXP(TimeSpan.FromHours(0.5));
    TimeSpan dootime = TimeSpan.FromHours(0.5);
    TimeSpan UPPHITUN = TimeSpan.FromHours(5.0);
    bool S = true;
    Process action;
    public Sim(Simulation env)
    {
        Console.WriteLine("Hallo fra construc");
        action = env.Process(sim(env));
    }
    public IEnumerable<Event> sim(Simulation env)
    {
        Console.WriteLine("Kominn í sim");
        while (true)
        {
            Console.WriteLine(env.Now);
            yield return env.Timeout(dootime);
            if (env.ActiveProcess.HandleFault())
            {
                Console.WriteLine($"Búið á tíma {env.Now}");
                calcData();
                Console.WriteLine("bunir að reikna");
            }
        }
    }
    public void calcData()
    {
        Console.WriteLine("Reiknum ehv");
    }
    public IEnumerable<Event> upphitunWait(Simulation env)
    {
        while (true)
        {
            Console.WriteLine("Hallo? fra upphitunwait");
            yield return env.Timeout(UPPHITUN);
            action.Interrupt();
            Console.WriteLine("Still here");
        }
    }
}
public class RunProg
{
    public static void Main(string[] args)
    {
        Console.WriteLine("Hallo?");
        Simulation env = new Simulation();
        Sim hund = new Sim(env);
        env.Process(hund.upphitunWait(env));
        //env.Run(hund.SIMTIME);
        LogNormal lognorm = new LogNormal(0.5, 1.0);
        lognorm.
    }
}