import turtle as bob

import numpy as np


class Point:
    # x - right to left, y- up to down
    x = y = z = 0

    def __init__(self) -> None:
        pass

    def __init__(self, x, y, z) -> None:
        self.x, self.y, self.z = x, y, z

    def distance(self, other):
        x = self.x - other.x
        y = self.y - other.y 
        z = self.z - other.z

        return x, y, z


class Rotation:
    x = y = z = 0

    def __init__(self) -> None:
        pass

    def __init__(self, x, y, z) -> None:
        self.x, self.y, self.z = x, y, z


def calc_rotation(s_pos: Point, t_pos: Point, s_rotation: Rotation):
    x, _, z = s_pos.distance(t_pos)
    goal = np.arctan2(z, x)

    rot = goal + s_rotation.y

    return rot


def cross(size):
    pos = bob.pos()
    bob.goto(pos[0] + size, pos[1])
    bob.goto(pos[0] - size, pos[1])
    bob.goto(pos[0], pos[1])
    bob.goto(pos[0], pos[1] - size)
    bob.goto(pos[0], pos[1] + size)
    bob.goto(pos[0], pos[1])

def rad_to_deg(x):
    # 1rad = 180/pi

    return 180 * x / np.pi

def draw(p_pos, t_pos, t_rot, rot):
    bob.penup()
    bob.goto(-p_pos[0], p_pos[1])
    bob.pencolor = "red"
    bob.pendown()
    cross(10)

    bob.penup()
    bob.goto(-t_pos[0], t_pos[1])
    bob.pencolor = "green"
    bob.pendown()
    cross(10)
    
    bob.right(rad_to_deg(t_rot - rot))
    bob.forward(200)


def main():
    p_pos = np.random.randint(-100, 101, size=2)
    t_pos = np.random.randint(-100, 101, size=2)

    rot =  Rotation(0, np.random.rand() * 2 * np.pi - np.pi, 0)
    # rot.y = 0
    print(rot.y)
    y = rot.y

    rot = calc_rotation(Point(t_pos[0], 10, t_pos[1]), Point(
        p_pos[0], 10, p_pos[1]),rot)
    draw(p_pos, t_pos, rot, y)

    input()


if __name__ == "__main__":
    main()
