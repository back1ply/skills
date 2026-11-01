namespace Sample.Shapes;
public abstract class Shape {
    public int Width;
    protected Shape() { Init(); }
    protected abstract void Init();
    public static int Count;
}
public class Box : Shape {
    protected override void Init() { }
    public int Area(int a, int b, int c, int d, int e) {
        int x = 0;
        if (a > 1 && b > 2 || c > 3) x = 42;
        switch (a) { case 1: x++; break; case 2: x--; break; }
        for (int i = 0; i < a; i++) { if (i % 2 == 0) x++; else if (i % 3 == 0) x--; else if (i % 5 == 0) x += 7; }
        while (x > 100) { x /= 2; if (x == 50) break; }
        try { x = x / b; } catch (System.Exception) { }
        return x;
    }
}
