namespace SimProj;

public class DataFinal
{
    public Dictionary<string, int[]> fjoldiDag;
    public Dictionary<string, int> maxInni = new Dictionary<string, int>();
    public Dictionary<string[], List<int>> deildAgeAmount;
    public List<double> LeguAmount;
    public int HeildarPatient;
    public Dictionary<(string,string), int> JobNum;
    public Dictionary<(string,string), int> SankeyData;
    public DataFinal(List<List<string>> keys)
    {
        SankeyData = new Dictionary<(string,string), int>();
        fjoldiDag = new Dictionary<string, int[]>();
        deildAgeAmount = new Dictionary<string[], List<int>>();
        foreach(List<string> lst_key in keys)
        {
            string[] keyArr = { lst_key[0] , lst_key[1] };
            deildAgeAmount.Add(keyArr, new List<int>());
        }
        LeguAmount = new List<double>();
    }

    public void Log()
    {
        File.AppendAllText(Run.pth, "Gögn um kerfið:" + Environment.NewLine);
        foreach(string key in maxInni.Keys)
        {
            File.AppendAllText(Run.pth,$"Lykill {key} og max inni eru {maxInni[key]}" + Environment.NewLine);
        }
        foreach((string,string) key in JobNum.Keys)
        {
            File.AppendAllText(Run.pth, $"Lykill {key} og starfsþörf: {JobNum[key]}" + Environment.NewLine);
        }
        foreach(string state in fjoldiDag.Keys)
        {
            File.AppendAllText(Run.pth, $"Deild {state} og fjöldi sem kom inn á hverjum degi:" + Environment.NewLine);
            foreach(int fj in fjoldiDag[state])
            {
                File.AppendAllText(Run.pth, fj.ToString() + Environment.NewLine);
            }
        }
    }
}
