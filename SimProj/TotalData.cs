namespace SimProj;
//Þessi class heldur utan um lokatölur um alla hermunina, 

public class TotalData
{
    public List<double> MeanLega;
    public Dictionary<(string,string), List<int>> Sankey;
    public List<int> totalPatient;
    public Dictionary<(string,string),List<double>> BoxPlot;
    public Dictionary<(string,string), List<int>> StarfsInfo;

    public TotalData(SimAttribs simAttr)
    {
        MeanLega = new List<double>();
        totalPatient = new List<int>();
        BoxPlot = new Dictionary<(string,string), List<double>>();
        StarfsInfo = new Dictionary<(string,string), List<int>>();
        foreach ((string,string) keys in simAttr.JobDemand.Keys)
        {
            StarfsInfo.Add(keys, new List<int>());
        }
        foreach (List<string> keyList in simAttr.Keys)
        {
            (string, string) keyTup = (keyList[0], keyList[1]);
            BoxPlot.Add(keyTup, new List<double>());
        }
    }
}
