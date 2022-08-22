#transform the G-code
import numpy as np
import operator


def get_cg_vector(file_name):  # return the coordinates of the slope vector for all points at their positions in the skeleton line
    file = open(file_name, 'r')
    result = []
    for n in file.read().split():
        if n[0] in {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '-'}:
            result.append(round(float(n), 5))
        if n == 'e':
            break
    data = []
    print(f'文件读取完毕，一共会生成{int(len(result) / 3)}个截面')
    if len(result) % 3 == 0:
        nums = [n for n in range(0, len(result)) if n % 3 == 0]
        for i in nums:
            data.append([result[i], result[i + 1], result[i + 2]])
    return data


def get_slice(file_name):  # read the information of the points after sliced and the number of points in each layer
    file = open(file_name, 'r')
    result = []
    for n in file.read().split():
        if n[0] == '[':
            break
        else:
            result.append(round(float(n), 4))
    data = []
    if len(result) % 3 == 0:
        nums = [n for n in range(0, len(result)) if n % 3 == 0]
        for i in nums:
            data.append([result[i], result[i + 1], result[i + 2]])
    file.close()

    with open(file_name, 'r') as f:
        context = f.readlines()
    target_line = 0
    for l in context:
        if l.find('[') != -1:
            break
        target_line += 1
    line = eval(context[target_line])
    f.close()
    return data, line


def distance(a, b, c):
    return (a * a + b * b + c * c) ** 0.5

def distance(a, b):
    return (a * a + b * b) ** 0.5


def Tran(x, y, z):
    return np.array([[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]])


def Rot(x, y):
    RotA = np.array([[1, 0, 0, 0], [0, np.cos(x), np.sin(x), 0], [0, -np.sin(x), np.cos(x), 0], [0, 0, 0, 1]])
    RotB = np.array([[np.cos(x), 0, -np.sin(x), 0], [0, 1, 0, 0], [np.sin(x), 0, np.cos(x), 0], [0, 0, 0, 1]])
    RotC = np.array([[np.cos(y), np.sin(y), 0, 0], [-np.sin(y), np.cos(y), 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    return np.dot(RotC, RotA)


def angle(cg_vector_data, i):  # compute the rotation angle of A-axis and C-axis
    dx = cg_vector_data[i][0]
    dy = cg_vector_data[i][1]
    dz = cg_vector_data[i][2]
    if dz == 0:
        dz = 0.00001
    theta = np.arctan(distance(dx, dy)/dz) /36
    if dy == 0:
        dy = 0.00001
    if dy > 0:
        delta = 2 * np.pi - np.arctan(abs(dx / dy))
    else:
        delta = np.pi + np.arctan(abs(dx / dy))
    return [theta, delta]


def calculate(slice_data, link_data, i, theta, delta):  # matrix transformation
    point = []
    new_point = []
    first = 0
    for j in range(i):
        first += link_data[j]
    last = first + link_data[i]
    for k in range(first, last):
        point.append(slice_data[k])
    Trana = Tran(0, 0, 0)
    Tranb = Tran(0, 0, 0)
    R = Rot(theta, delta)
    T = np.dot(R, Trana)
    M = np.dot(Tranb, T)
    for m in range(len(point)):
        new_point.append(np.dot(M, np.array([[point[m][0]], [point[m][1]], [point[m][2]], [1]])))
    return new_point


def main():
    cg_vector_data = get_cg_vector('C:/Users/DELL/Desktop/Program/final_test/skeleton_vector.txt')
    trans_file = 'C:/Users/DELL/Desktop/Program/final_test/Gcode2.txt'
    f = open(trans_file, 'w')
    slice_data, link_data = get_slice('C:/Users/DELL/Desktop/Program/final_test/Coordinates2.txt')
    for i in range(len(link_data)):
        p = angle(cg_vector_data, i)                                 # compute the A- and C-axis of slices in each layer
        new_point = calculate(slice_data, link_data, i, p[0], p[1])  # compute the coordinates of points after slicing and matrix transformation
        for j in range(len(new_point)):
            x = np.round(new_point[j][0][0], 2)
            y = np.round(new_point[j][1][0], 2)
            z = np.round(new_point[j][2][0], 2)
            a = np.round(180 * p[0] / np.pi, 2)
            c = np.round(180 * p[1] / np.pi, 2)
            result = [x,y,z,a,c]
            f.write("G01"+"\t"+"X"+" "+str(result[0]) + "\t"+"Y"+" "+str(result[1]) + "\t"+"Z"+" "+str(result[2]) + "\t"+"A"+" "+str(result[3]) + "\t"+"C"+" "+str(result[4]) + "\t"+"\n")
    print('写入数据完成')
    f.close()


if __name__ == '__main__':
    main()
