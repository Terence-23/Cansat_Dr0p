import sys
import numpy as np
import logging as log
import os


def multiplyMat(matrix1, matrix2):
    if len(matrix1[0]) != len(matrix2):
        return
    wynMat = [[0 for _ in range(len(matrix2))] for _ in range(len(matrix1))]

    for i in range(len(matrix1)):
        for j in range(len(matrix2[i])):
            tmpSum = 0
            for k in range(len(matrix1[i])):
                tmpSum += matrix1[i][k] * matrix2[k][j]
            wynMat[i][j] = tmpSum

    return wynMat


def multiplyVec(matrix, vec):
    if len(vec) != len(matrix[0]):
        return
    wynVec = [0 for _ in range(len(matrix))]
    for i in range(len(matrix)):
        tmpSum = 0
        for j in range(len(vec)):
            tmpSum += vec[j] * matrix[i][j]
        wynVec[i] = tmpSum

    return wynVec


def degToRad(deg):
    return deg/180 * np.pi


def rotateVec(vec, xAngle=0, yAngle=0, zAngle=0, isDeg=True):

    # vec - vector to rotate
    # x/z/y_angle - angle to rotate over the respective axis
    # isDeg - if true it needs to be converted to radians

    if isDeg:
        xAngle = degToRad(xAngle)
        yAngle = degToRad(yAngle)
        zAngle = degToRad(zAngle)

    x_matrix = [[1, 0, 0],
                [0, np.cos(xAngle), -np.sin(xAngle)],
                [0, np.sin(xAngle), np.cos(xAngle)]]
    y_matrix = [[np.cos(yAngle), 0, np.sin(yAngle)],
                [0, 1, 0],
                [-np.sin(yAngle), 0, np.cos(yAngle)]]
    z_matrix = [[np.cos(zAngle), -np.sin(zAngle), 0],
                [np.sin(zAngle), np.cos(zAngle), 0],
                [0, 0, 1]]

    rotMat = multiplyMat(multiplyMat(z_matrix, y_matrix), x_matrix)
    return multiplyVec(rotMat, vec)


def getData(fPath):
    wind.info(f"Reading data from file: \n {fPath}")
    with open(fPath) as f:
        data = f.readlines()
    wind.debug("Data read:")
    for i, v in enumerate(data):
        v = [np.float128(float(j)) for j in v[:-2].split(';')]
        data[i] = v
        wind.debug(data[i])

    return data


def rotateData(data, isDeg=True):
    rotated = []
    for i in data:
        vec = i[0:3]
        x, y, z = i[3:6]
        log.debug("Rotating vector")
        log.debug(x, y, z)
        vec = rotateVec(vec, -x, -y, -z, isDeg)
        rotated.append(vec)
    wind.debug(rotated[0])
    return rotated
    


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs='?', default="data/test.data",
                        help="path to data file - absolute or local, default: data/test.data")
    parser.add_argument("-l", "--log", default="info",
                        help="Level of logging. Available values: debug, info, warning, error")
    args = parser.parse_args()
    if args.path[0] == "/" \
            or args.path[1] == ':' \
            or args.path[0:2] == "~/":
        dPath = args.path
    elif args.path[0:2] == "./":
        dPath = os.getcwd() + args.path[2:]
    elif args.path[0:3] == "../":
        log.error("try using absolute path")
        sys.exit()
    else:
        dPath = os.getcwd() + args.path

    # Log setup
    loglevel = args.log
    numeric_level = getattr(log, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)

    log.basicConfig(level=numeric_level, filename=args.path + '.log')
    wind = log.getLogger("wind")
    wind.setLevel(numeric_level)
    log.info("Program start")
    # Log ready

    # expected data format: acceleration x;y;z  world rotaiton x;y;z in degrees
    data = getData(os.getcwd() + "/data/test.data")
    if len(data) < 1:
        raise ValueError("No data read from selected file")

    # rotating data to world axis
    rotateData(data)
