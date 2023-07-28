namespace Test;
using System.Diagnostics;
public class Hundur
{
    public static void Main(string[] args)
    {
        List<List<string>> hundaList = new List<List<string>>(); 
        Dictionary<string[], List<int>> hundaTest = new Dictionary<string[], List<int>>();
        hundaList.Add(new List<string>());
        hundaList.Add(new List<string>());
        hundaList.Add(new List<string>());
        hundaList[0].Add("Hundur");
        hundaList[0].Add("Köttur");
        hundaList[1].Add("Toopy");
        hundaList[1].Add("Sköttur");
        hundaList[2].Add("Ploopy");
        hundaList[2].Add("Möttur");
        foreach(List<string> listKey in hundaList)
        {
            string[] keyArr = { listKey[0], listKey[1] };
            hundaTest.Add(keyArr, new List<int>());
        }
        foreach (string[] key in hundaTest.Keys)
        {
            Console.WriteLine($"key item 1: {key[0]} og 2: {key[1]}");
        }
        for (int i = 0; i < 5; i++)
        {
            foreach (string[] listCheck in hundaTest.Keys)
            {
                hundaTest[listCheck].Add(i);
            }
        }
        foreach (string[] key in hundaTest.Keys)
        {
            Console.WriteLine($"key: {key} með val: {hundaTest[key]}");
        }
    }
}