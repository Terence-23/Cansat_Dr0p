#include <iostream>
#include <math.h>
#include "processData.h"
#define _USE_MATH_DEFINES

#ifndef M_PI
#define M_PI 3.14159265
#endif

#define pb push_back

using namespace std;

const char sep = ';';


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