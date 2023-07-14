/* Þessi class hermir deildir kerfisins 
 * 
 */

using SimSharp;

namespace SimProj;
public class Deild
{
    private DeildInfo dataDeild = new DeildInfo();
    private Kerfi S;
    private string nafn;
    private Simulation env;
    public Deild(Simulation envment, Kerfi kerfi, string Nafn)
    {
        env = envment;
        S = kerfi;
        nafn = Nafn;
    }
}

