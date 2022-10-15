#include "Point.h"
#include <math.h>

// FIXME: remove declarations below and get some actual data in place.
double base_temperature, Lb, preassure, base_preassure, R, g, M;

// calculate height of the cansat
double calc_height()
{
    // Pb = static pressure (pressure at sea level) [Pa]
    // Tb = standard temperature (temperature at sea level) [K]
    // Lb = standard temperature lapse rate [K/m] = -0.0065 [K/m]
    // h = height about sea level [m]
    // R = universal gas constant = 8.31432
    // g0 = gravitational acceleration constant = 9.80665
    // M = molar mass of Earth’s air = 0.0289644 [kg/mol]

    // h = (Tb/Lb) * ((P/Pb)^(-R*Lb/g0*M) - 1)
    double h = (base_temperature / Lb) * (pow(preassure/base_preassure, -R*Lb/g*M) -1);
    return h;
}



// calculate angle for the cansat to rotate
double calc_rotation(Point p_pos, Point t_pos, double rot)
{   
    // p_pos = pos of cansat
    // t_pos = pos of target
    // rot = cansat rotation
    double x = t_pos.x - p_pos.x, z = t_pos.z - p_pos.z;
    double goal = atan2(z, x);
    // cerr << goal << ' ' << x << ' ' << z;

    return goal + rot;
}