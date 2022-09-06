#include <iostream>
#include <math.h>
#define _USE_MATH_DEFINES

#define pb push_back

using namespace std;

const char sep = ';';

class Point
{
public:
    double x, y, z;
    Point(double x, double y, double z);

    double distance_s(Point other)
    {
        double x, y, z, dist;
        x = this->x - other.x;
        y = this->y - other.y;
        z = this->z - other.z;
        dist = sqrt(x * x + y * y + z * z); 
        return dist;
    }
};

Point::Point(double x, double y, double z)
{
    this->x = x;
    this->y = y;
    this->z = z;
}


double calc_rotation(Point p_pos, Point t_pos, double rot)
{
    
    double x = t_pos.x - p_pos.x, z = t_pos.z - p_pos.z;
    double goal = atan2(z, x);
    // cerr << goal << ' ' << x << ' ' << z;

    return goal + rot;
}

int main()
{
    double rot, p1, p2, t1, t2;
    cin >> p1 >> p2 >> t1 >> t2 >> rot;
    Point p_pos = Point(p1, 10, p2), t_pos = Point(t1, 10, t2);
    double wyn = calc_rotation(p_pos, t_pos, rot);
    cout << wyn << '\n';
    cerr << wyn * 180 / M_PI<< '\n';
    return 0;
}