namespace SimProj;

public class DataFinal
{
    public Dictionary<(string,string), int[]> fjoldiDag;
    public Dictionary<string, int> maxInni = new Dictionary<string, int>();
    public Dictionary<(string,string), List<int>> deildAgeAmount;
    public List<double> LeguAmount;
    public int HeildarPatient;
    public Dictionary<(string,string), int> JobNum;
    public Dictionary<(string,string), int> SankeyData;
    public DataFinal(List<List<string>> keys)
    {
        SankeyData = new Dictionary<(string,string), int>();
        fjoldiDag = new Dictionary<(string,string), int[]>();
        deildAgeAmount = new Dictionary<(string,string), List<int>>();
        foreach(List<string> lst_key in keys)
        {
            (string, string) key_tup = (lst_key[0], lst_key[1]);
            deildAgeAmount.Add(key_tup, new List<int>());
        }
        LeguAmount = new List<double>();
    }

    public void Log()
    {
        Console.WriteLine("Gögn um kerfið:" + Environment.NewLine);
        foreach(string key in maxInni.Keys)
        {
            Console.WriteLine($"Lykill {key} og max inni eru {maxInni[key]}" + Environment.NewLine);
        }
        foreach((string,string) key in JobNum.Keys)
        {
            Console.WriteLine($"Lykill {key} og starfsþörf: {JobNum[key]}" + Environment.NewLine);
        }
        foreach((string,string) kvp in fjoldiDag.Keys)
        {
            Console.WriteLine($"Deild {kvp.Item2} og fjöldi sem kom inn á hverjum degi:" + Environment.NewLine);
            foreach(int fj in fjoldiDag[kvp])
            {
                Console.WriteLine(fj.ToString() + Environment.NewLine);
            }
        }
    }
}
