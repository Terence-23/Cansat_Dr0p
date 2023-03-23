import haversine
import math


def calc_antenna_angle(ant_pos, goal_pos, goal_alt, degrees=True):

    """Calculate angles for antenna rotation  to goal pointreturn angles alfa and beta
    alfa - angle of rotation horizontally from north
    beta - angle of rotation vertically 
    
    ant_pos - gps position of antenna
    goal_pos - gps position of point to aim at
    goal_alt - altitude (in meters) of goal point above antenna
    """


    alfa = math.atan2(goal_pos[1] -ant_pos[1],goal_pos[0] - ant_pos[0])

    dist = haversine.haversine_distance(ant_pos, goal_pos, haversine.Unit.METERS)
    beta = math.atan2(goal_alt, dist)
    
    if degrees:
        return math.degrees(alfa), math.degrees(beta)
    else:
        return alfa, beta
    
def main():
    ant = (0, 0)
    north = (1, 0)
    south = (-1, 0)
    east = (0, 1)
    west = (0, -1)
    
    res = [calc_antenna_angle(ant, i, haversine.haversine_distance(ant, north, haversine.Unit.METERS)) for i in [north, east, south, west]]
    
    
    print(f'beta = 45deg res: {res}')
    
    res = [calc_antenna_angle(ant, i, 0) for i in [north, east, south, west]]
    print(f'beta = 0deg res: {res}')
    
    
if __name__ == '__main__':
    main()
