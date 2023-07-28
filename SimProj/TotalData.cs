namespace SimProj;
//Þessi class heldur utan um lokatölur um alla hermunina, 

public class TotalData
{
    public List<int> SpitaliAmount;
    public List<double> MeanLega;
    public Dictionary<string[], int> Sankey;
    public List<double> ConfInter;
    public List<int> totalPatient;
    public Dictionary<string[],double> BoxPlot;
    public Dictionary<(string,string), List<int>> StarfsInfo;

    public TotalData(SimAttribs simAttr)
    {
        MeanLega = new List<double>();
        totalPatient = new List<int>();
        BoxPlot = new Dictionary<string[], double>();
        StarfsInfo = new Dictionary<(string,string), List<int>>();
        foreach ((string,string) keys in simAttr.JobDemand.Keys)
        {
            StarfsInfo.Add(keys, new List<int>());
        }
    }
}
