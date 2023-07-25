/*
    Þessi class heldur utan um upplýsingar um sjúklinginn.

    
 */

namespace SimProj;
public class Patient
{
    private string aldur;
    private string deild;
    private double timiSpitala;
    private int numer;
    public Patient(string age, string state, int number)
    {
        aldur = age;
        deild = state;
        timiSpitala = 0.0;
        numer = number;
    }
    public string Aldur
    {
        get { return aldur; }
        set { aldur = value; }
    }
    public string Deild
    {
        get { return deild; }
        set { deild = value; }
    }
    public int Numer
    {
        get { return numer; }
    }
    public double TimiSpitala
    {
        get { return timiSpitala;}
        set { timiSpitala = value;}
    }
}

