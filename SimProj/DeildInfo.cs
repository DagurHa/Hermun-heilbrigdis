/*
    Þessi skrá heldur utan um upplýsingar deildar
 */
namespace SimProj;

public struct DeildInfo
{
    public List<int> fjoldiDag = new List<int>(); //Fjöldi sjúklinga sem koma inn yfir daginn
    public int maxInni; //Hámarksfjöldi sjúklinga sem voru inni yfir hermunina
    public List<int> fjoldiInniDag = new List<int>(); //Fjöldi sjúklinga inni á enda dags
    public DeildInfo() { }
}