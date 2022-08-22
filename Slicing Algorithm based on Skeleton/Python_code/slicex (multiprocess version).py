import sympy as sy
import operator
import multiprocessing
from itertools import chain
import time


x, y, z = sy.symbols('x y z')
# order_tri_data = []
# fig = plt.figure(1)
# ax = fig.gca(projection='3d')
file_handle = open('G:/大三下/项目管理/代码/插值/slice_datax.txt', mode='w')  # write in txt document


class Plane:  # define the plane class used in slicing
    def __init__(self, vector=[0, 0, 0], point_1=[0, 0, 0]):
        self.__vector = vector
        self.__point_1 = point_1

    @property
    def vector(self):
        return self.__vector  # normal vector of the plane

    @property
    def point_1(self):
        return self.__point_1  # the point on the plane


class Triangle:  # define the triangle patches class
    def __init__(self, vector=[0, 0, 0], point_1=[0, 0, 0], point_2=[0, 0, 0], point_3=[0, 0, 0], order=-1,
                 connect=[]):  # "order" is the No. of triangles, "connect" is the No. of its neighbor triangles
        self.__vector = vector
        self.__point_1 = point_1
        self.__point_2 = point_2
        self.__point_3 = point_3
        self.__order = order
        self.__connect = connect

    def changeconnect(self, i):
        self.__connect.append(i)

    def set_order(self, order):
        self.__order = order

    @property
    def vector(self):
        return self.__vector

    @property
    def point_1(self):
        return self.__point_1

    @property
    def point_2(self):
        return self.__point_2

    @property
    def point_3(self):
        return self.__point_3

    @property
    def order(self):
        return self.__order

    @property
    def connect(self):
        return self.__connect


def get_distance(node, pla):  # get the distance between point and plane
    plane_a = get_plane(pla.point_1, pla.vector)
    test = plane_a.evalf(subs={x: node[0], y: node[1], z: node[2]})
    test = float(test)
    return test


def get_plane(point, normal):  # the plane equation
    plane = f'(x-{point[0]})*{normal[0]} + (y-{point[1]})*{normal[1]} + (z-{point[2]})*{normal[2]}'
    plane = sy.sympify(plane)
    return plane


def get_inter(planevector, planepoint, linevector, linepoint):  # get the intersection of line and plane
    vp1 = planevector[0]
    vp2 = planevector[1]
    vp3 = planevector[2]
    n1 = planepoint[0]
    n2 = planepoint[1]
    n3 = planepoint[2]
    v1 = linevector[0]
    v2 = linevector[1]
    v3 = linevector[2]
    m1 = linepoint[0]
    m2 = linepoint[1]
    m3 = linepoint[2]
    vpt = v1 * vp1 + v2 * vp2 + v3 * vp3
    t = ((n1 - m1) * vp1 + (n2 - m2) * vp2 + (n3 - m3) * vp3) / vpt
    return [round((m1 + v1 * t), 4), round((m2 + v2 * t), 4), round((m3 + v3 * t), 4)]


def get_intersection(tri, pla):  # get the intersections of a triangle patch and a plane
    intersection = []
    if get_distance(tri.point_1, pla) == 0:  # given that we focus on pipes, we don't take the special situation into
                                             # account that a patch is exactly on the plane
        intersection.append(tri.point_1)
    if get_distance(tri.point_2, pla) == 0:
        intersection.append(tri.point_2)
    if get_distance(tri.point_3, pla) == 0:
        intersection.append(tri.point_3)
    if get_distance(tri.point_1, pla) * get_distance(tri.point_2, pla) < 0:
        intersection.append(get_inter(pla.vector, pla.point_1,
                                      [tri.point_1[0] - tri.point_2[0], tri.point_1[1] - tri.point_2[1],
                                       tri.point_1[2] - tri.point_2[2]], tri.point_1))
    if get_distance(tri.point_1, pla) * get_distance(tri.point_3, pla) < 0:
        intersection.append(get_inter(pla.vector, pla.point_1,
                                      [tri.point_1[0] - tri.point_3[0], tri.point_1[1] - tri.point_3[1],
                                       tri.point_1[2] - tri.point_3[2]], tri.point_1))
    if get_distance(tri.point_2, pla) * get_distance(tri.point_3, pla) < 0:
        intersection.append(get_inter(pla.vector, pla.point_1,
                                      [tri.point_2[0] - tri.point_3[0], tri.point_2[1] - tri.point_3[1],
                                       tri.point_2[2] - tri.point_3[2]], tri.point_2))
    return intersection


def get_data(file_name):  # input: stl document, output: a list consisting of all triangle objects
    file = open(file_name, 'r')
    points = []
    for n in file.read().split():
        if n[0] in {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '-'}:
            points.append(round(float(n), 4))
    file.close()
    data = []
    nums = [n for n in range(len(points)) if n % 12 == 0]
    for n in nums:
        e = Triangle(vector=[points[n], points[n + 1], points[n + 2]],
                     point_1=[points[n + 3], points[n + 4], points[n + 5]],
                     point_2=[points[n + 6], points[n + 7], points[n + 8]],
                     point_3=[points[n + 9], points[n + 10], points[n + 11]],
                     order=int(n / 12 + 1))
        data.append(e)
    return data  # data is a list of triangles


def get_intersection_triangle(tri, pla):  # input: list of triangle patches and the plane, fc: find out which
                                          # triangles intersect with the plane, output: the intersected triangles
    new_tri = []
    i = 0
    for i in range(0, len(tri)):
        if get_distance(tri[i].point_1, pla) > 0 and get_distance(tri[i].point_2, pla) > 0 and get_distance(
                tri[i].point_3, pla) > 0:
            continue
        if get_distance(tri[i].point_1, pla) < 0 and get_distance(tri[i].point_2, pla) < 0 and get_distance(
                tri[i].point_3, pla) < 0:
            continue
        if get_distance(tri[i].point_1, pla) == 0 and get_distance(tri[i].point_2, pla) < 0 and get_distance(
                tri[i].point_3, pla) < 0:
            continue
        if get_distance(tri[i].point_1, pla) < 0 and get_distance(tri[i].point_2, pla) == 0 and get_distance(
                tri[i].point_3, pla) < 0:
            continue
        if get_distance(tri[i].point_1, pla) < 0 and get_distance(tri[i].point_2, pla) < 0 and get_distance(
                tri[i].point_3, pla) == 0:
            continue
        if get_distance(tri[i].point_1, pla) == 0 and get_distance(tri[i].point_2, pla) > 0 and get_distance(
                tri[i].point_3, pla) > 0:
            continue
        if get_distance(tri[i].point_1, pla) > 0 and get_distance(tri[i].point_2, pla) == 0 and get_distance(
                tri[i].point_3, pla) > 0:
            continue
        if get_distance(tri[i].point_1, pla) > 0 and get_distance(tri[i].point_2, pla) > 0 and get_distance(
                tri[i].point_3, pla) == 0:
            continue
        new_tri.append(tri[i])
    return new_tri


def get_cg(file_name):  # return all points of the skeleton line of the model
    file = open(file_name, 'r')
    result = []
    for n in file.read().split():
        if n[0] in {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '-'}:
            result.append(round(float(n), 4))
        if n == 'e':
            break
    data = []
    # print(len(result))
    if len(result) % 3 == 0:
        nums = [n for n in range(0, len(result)) if n % 3 == 0]
        for i in nums:
            data.append([result[i], result[i + 1], result[i + 2]])
    data.sort(key=operator.itemgetter(2))
    return data


def get_cg_vector(file_name):  # return the slope vector coordinates of all points of the skeleton at their positions
    file = open(file_name, 'r')
    result = []
    for n in file.read().split():
        if n[0] in {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '-'}:
            result.append(round(float(n), 5))
    data = []
    print(f'文件读取完毕，一共会生成{int(len(result) / 3)}个截面')
    if len(result) % 3 == 0:
        nums = [n for n in range(0, len(result)) if n % 3 == 0]
        for i in nums:
            data.append([result[i], result[i + 1], result[i + 2]])
    return data


def run(num, first, last, tri_data, cg_data, cg_vector_data, p, link):
    print(f'第{num + 1}个进程启动！')
    for i in range(first, last + 1):
        pla = Plane(vector=cg_vector_data[i], point_1=cg_data[i])
        new_tri_data = get_intersection_triangle(tri_data, pla)
        point_section = []
        for n in new_tri_data:
            inter = get_intersection(n, pla)
            point_section.append(inter[0])
            point_section.append(inter[1])
            '''
            for j in temp:
                if j not in p:
                    p.append(j)
                    k += 1
            '''
        p.append(point_section[0])  # the list of points on one plane after ordering
        k = 1                       # counter of points in each layer
        count = 0
        goal = point_section[0]

        while count < int(len(point_section) / 2):  # order the points
            for num1 in range(0, len(point_section)):
                if point_section[num1] == goal:
                    if num1 % 2 == 0:
                        goal = point_section[num1 + 1]
                        point_section[num1 + 1] = 0
                        p.append(goal)
                        k += 1
                    if num1 % 2 == 1:
                        goal = point_section[num1 - 1]
                        point_section[num1 - 1] = 0
                        p.append(goal)
                        k += 1
                    if goal == point_section[0]:
                        count = len(point_section)  # stop the loop
        print(f'第{i + 1}个截面已产生')
        link.append(k)
    print(f'第{num + 1}个进程已完成')


def main():                             # multiprocessing to speed up the computation
    start = time.process_time()
    print(start)
    tri_data = get_data('G:/大三下/项目管理/代码/tube3.stl')
    cg_data = get_cg('G:/大三下/项目管理/代码/插值/skeleton.txt')
    cg_vector_data = get_cg_vector('G:/大三下/项目管理/代码/插值/skeleton_vector.txt')
    print('提取stl与cg文件完成！')
    with multiprocessing.Manager() as manager:
        p = [[] for _ in range(10)]
        link = [[] for _ in range(10)]
        for m in range(10):
            p[m] = manager.list()
        for n in range(10):
            link[n] = manager.list()
        print('创建进程列表完成！')
        pro = []
        for i in range(10):
            pro.append(multiprocessing.Process(target=run,
                                               args=(i, i * (len(cg_data) // 10), (i + 1) * (len(cg_data) // 10) - 1, tri_data, cg_data, cg_vector_data, p[i], link[i],)))
            pro[i].daemon = True
        print('创建进程完成！')
        for j in range(10):
            pro[j].start()
        for k in range(10):
            pro[k].join()
        for a in range(10):
            for b in p[a]:
                for c in b:
                    file_handle.write(str(c) + ' ')
                file_handle.write('\n')
        link_list = list(chain(*link))
        file_handle.write(str(link_list))
    print('写入数据完成')
    file_handle.close()
    end = time.process_time()
    print("运行时间为：", end - start)


if __name__ == '__main__':
    main()
