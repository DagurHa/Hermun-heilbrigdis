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
    public Dictionary<string[], List<int>> StarfsInfo;

    public TotalData(SimAttribs simAttr)
    {
        BoxPlot = new Dictionary<string[], double>();
        StarfsInfo = new Dictionary<string[], List<int>>();
        foreach ((string,string) keys in simAttr.JobDemand.Keys)
        {
            string[] sInfoKey = {keys.Item1,keys.Item2};
            StarfsInfo.Add(sInfoKey, new List<int>());
        }
    }
}
