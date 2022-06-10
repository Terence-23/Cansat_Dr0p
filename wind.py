import numpy as np


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

def rotateVec(vec, x_angle = 0 , y_angle = 0, z_angle = 0, is_Deg = True):
    if is_Deg:
        x_angle = degToRad(x_angle)
        y_angle = degToRad(y_angle)
        z_angle = degToRad(z_angle)
    x_matrix = [[1, 0, 0],
                [0, np.cos(x_angle), -np.sin(x_angle)],
                [0, np.sin(x_angle), np.cos(x_angle)]]
    y_matrix = [[np.cos(y_angle), 0, np.sin(y_angle)],
                [0, 1, 0],
                [-np.sin(y_angle), 0, np.cos(y_angle)]]
    z_matrix = [[np.cos(z_angle), -np.sin(z_angle), 0],
                [np.sin(z_angle), np.cos(z_angle), 0],
                [0, 0, 1]]
    
    rotMat = multiplyMat(multiplyMat(z_matrix, y_matrix), x_matrix)
    return multiplyVec(rotMat, vec)    


if __name__ == "__main__":
    z_angle = degToRad(-90)
    z_matrix = [[np.cos(z_angle), -np.sin(z_angle), 0],
                [np.sin(z_angle), np.cos(z_angle), 0],
                [0, 0, 1]]
    
    print(multiplyVec(z_matrix, [0, 1, 0]))
    print(rotateVec([0, 1, 0], 0, 0, 0))
