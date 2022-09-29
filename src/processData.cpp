#include <math.h>
#include "processData.h"


double calc_rotation(Point p_pos, Point t_pos, double rot)
{   
    double x = t_pos.x - p_pos.x, z = t_pos.z - p_pos.z;
    double goal = atan2(z, x);
    // cerr << goal << ' ' << x << ' ' << z;

    return goal + rot;
}

double Point::distance_s(Point other)
{
        double x, y, z, dist;
        x = this->x - other.x;
        y = this->y - other.y;
        z = this->z - other.z;
        dist = sqrt(x * x + y * y + z * z); 
        return dist;
    }

Point::Point(double x, double y, double z)
{
    this->x = x;
    this->y = y;
    this->z = z;
}

