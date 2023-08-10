namespace SimProj;
//Þessi class heldur utan um lokatölur um alla hermunina, 

public class TotalData
{
    public List<Dictionary<(string,string), double>> meanTimeDeild; //Listi af meðaltímum á deild eftir aldri yfir allar hermanirnar
    public List<double> MeanLega; //Meðalfjöldi fólks á legudeild í enda dags
    public Dictionary<(string,string), List<int>> Sankey; //Gögn fyrir sankey rit, item1 er frá item2 er til
    public List<int> totalPatient; //Heildarfjöldi Sjúklinga sem kom í kerfið
    public Dictionary<(string,string),List<double>> BoxPlot; //useless
    public Dictionary<(string,string), List<int>> StarfsInfo;
    public Dictionary<(string, string), int[,]> MeanAmount; //Fjöldi fólks eftir aldurshópi og deild sem kom yfir dag fyrir alla daga   
    public TotalData(SimAttribs simAttr)
    {
        meanTimeDeild = new List<Dictionary<(string, string), double>>();
        MeanAmount = new Dictionary<(string, string), int[,]>();
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
            MeanAmount.Add(keyTup, new int[simAttr.SimAmount,simAttr.Stop]);
        }

    }
}
