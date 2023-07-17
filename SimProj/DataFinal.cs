using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SimProj;

public struct DataFinal
{
    public Dictionary<string, List<int>> fjoldiDag;
    public Dictionary<string, int> maxInni;
    public Dictionary<(string, string), List<int>> deildAgeAmount;
}
