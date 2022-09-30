

// const definitions
#define _USE_MATH_DEFINES
// gravitation constant
#define g 9.80665
// Lb = standard temperature lapse rate [K/m] = -0.0065 [K/m]
#define Lb -0.0065
// R = universal gas constant = 8.31432
#define R 8.31432
// M = molar mass of Earth’s air = 0.0289644 [kg/mol]
#define M 0.0289644

// variable values
double preassure  = 0;
double base_preassure = 0;
double base_temperature = 0;


// Point declare

class Point
{
public:
    double x, y, z;
    Point(double x, double y, double z);

    double distance_s(Point other);
};



// preassure -height
// P = gh(density)
double calc_height(); 

// rotation 
double calc_rotation(Point p_pos, Point t_pos, double rot);


