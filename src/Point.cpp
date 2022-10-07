#include "Point.h"
#include <math.h>

// get scalar distance from other point
double Point::distance_s(Point other)
{
        double x, y, z, dist;
        x = this->x - other.x;
        y = this->y - other.y;
        z = this->z - other.z;
        dist = sqrt(x * x + y * y + z * z); 
        return dist;
}

// create 3d point
Point::Point(double x, double y, double z)
{
    this->x = x;
    this->y = y;
    this->z = z;
}
