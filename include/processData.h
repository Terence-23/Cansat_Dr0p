

// const definitions
#define _USE_MATH_DEFINES
#define g 9.80665

// Point declare

class Point
{
public:
    double x, y, z;
    Point(double x, double y, double z);

    double distance_s(Point other);
};



// preassure -height

// rotation 
double calc_rotation(Point p_pos, Point t_pos, double rot);


