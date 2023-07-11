import numpy as np
import json


def create_json(points, triangles, wrong_triangles):

    point = []
    for i in range(len(points)):
        point.append({"x": points[i][0], "y": points[i][1]},)

    bad = []
    for i in range(len(wrong_triangles)):
        bad.append({"a": wrong_triangles[i][0], "b": wrong_triangles[i][1], "c": wrong_triangles[i][2]},)

    triangle = []
    for i in range(len(triangles)):
        triangle.append({"a": triangles[i][0], "b": triangles[i][1], "c": triangles[i][2]},)

    data = {"points": point, "triangles": triangle, "wrong": bad}

    with open("output.json", "w") as file:
        json.dump(data, file, indent=4)


def distance(point1, point2):
    x1, y1 = point1[0], point1[1]
    x2, y2 = point2[0], point2[1]
    return round((x2 - x1) ** 2 + (y2 - y1) ** 2, 2)


def get_lines(points):
    segments = []

    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            length = distance(points[i], points[j])
            segments.append((points[i], points[j], length))

    sorted_segments = sorted(segments, key=lambda x: x[2])
    return sorted_segments


def is_intersect(seg1, seg2):
    x1, y1, x2, y2 = seg1[0][0], seg1[0][1], seg1[1][0], seg1[1][1]
    x3, y3, x4, y4 = seg2[0][0], seg2[0][1], seg2[1][0], seg2[1][1]

    if (max(x1, x2) >= min(x3, x4) and max(x3, x4) >= min(x1, x2) and
            max(y1, y2) >= min(y3, y4) and max(y3, y4) >= min(y1, y2)):

        if (((x1 == x3) and (y1 == y3)) or ((x2 == x4) and (y2 == y4)) or
                ((x1 == x4) and (y1 == y4)) or ((x2 == x3) and (y2 == y3))):
            return False

        # Проверяем пересечение ребер, иначе используем формулу пересечения прямых
        d1 = (x4 - x3) * (y1 - y3) - (x1 - x3) * (y4 - y3)
        d2 = (x4 - x3) * (y2 - y3) - (x2 - x3) * (y4 - y3)
        d3 = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
        d4 = (x2 - x1) * (y4 - y1) - (x4 - x1) * (y2 - y1)

        if d1 * d2 < 0 and d3 * d4 < 0:
            return True

        return False
    else:
        return False


def greed(seg):
    tri = [seg[0]]
    for i in range(1, len(seg)):
        ch = True
        for j in range(len(tri)):
            if is_intersect(seg[i], tri[j]):
                ch = False
        if ch:
            tri.append(seg[i])
    return tri


def point_in_triangle(point, triangle):
    # Распаковываем вершины треугольника
    p1, p2, p3 = triangle

    # Вычисляем барицентрические координаты точки
    A = 0.5 * (-p2[1]*p3[0] + p1[1]*(-p2[0] + p3[0]) + p1[0]*(p2[1] - p3[1]) + p2[0]*p3[1])
    sign = 1 if A > 0 else -1
    s = (p1[1]*p3[0] - p1[0]*p3[1] + (p3[1] - p1[1])*point[0] + (p1[0] - p3[0])*point[1]) * sign
    t = (p1[0]*p2[1] - p1[1]*p2[0] + (p1[1] - p2[1])*point[0] + (p2[0] - p1[0])*point[1]) * sign
    return s > 0 and t > 0 and (s + t) < 2*A*sign


def find_triangles(edges, points):
    # Конвертируем входные данные в списки
    edges = [(list(edge[0]), list(edge[1])) for edge in edges]
    points = [list(point) for point in points]

    # Создаем пустой словарь смежности
    graph = {}
    for edge in edges:
        p1, p2 = tuple(edge[0]), tuple(edge[1])
        if p1 not in graph:
            graph[p1] = set()
        if p2 not in graph:
            graph[p2] = set()
        graph[p1].add(p2)
        graph[p2].add(p1)

    triangles = []
    for p1 in graph:
        for p2 in graph[p1]:
            for p3 in graph[p2]:
                if p3 in graph[p1]:
                    # Нашли треугольник
                    triangle = tuple(sorted([p1, p2, p3]))
                    # Проверяем, что все остальные точки находятся за пределами треугольника
                    is_valid_triangle = True
                    for point in points:
                        if point not in triangle and point_in_triangle(point, triangle):
                            is_valid_triangle = False
                            break
                    if is_valid_triangle and triangle not in triangles:
                        triangles.append(triangle)

    return triangles


def circle_from_points(triangle):
    p1 = triangle[0]
    p2 = triangle[1]
    p3 = triangle[2]

    temp = p2[0] ** 2 + p2[1] ** 2
    bc = (p1[0] ** 2 + p1[1] ** 2 - temp) / 2
    cd = (temp - p3[0] ** 2 - p3[1] ** 2) / 2
    det = (p1[0] - p2[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p2[1])

    if abs(det) < 1.0e-6:
        return None

    # Center of the circle
    cx = (bc * (p2[1] - p3[1]) - cd * (p1[1] - p2[1])) / det
    cy = ((p1[0] - p2[0]) * cd - (p2[0] - p3[0]) * bc) / det

    radius = np.sqrt((cx - p1[0]) ** 2 + (cy - p1[1]) ** 2)

    return cx, cy, radius


def get_circles(triangles):
    circles = []
    for i in range(len(triangles)):
        circles.append(circle_from_points(triangles[i]))
    return circles


def check_delaunay(triangles, points):
    wrong_triangles = []
    for triangle in triangles:
        circle = circle_from_points(triangle)
        if circle is None:
            continue
        for point in points:
            if np.array_equal(point, triangle[0]) or np.array_equal(point, triangle[1]) or np.array_equal(point, triangle[2]):
                continue
            if np.sqrt((point[0]-circle[0])**2 + (point[1]-circle[1])**2) < circle[2]:
                wrong_triangles.append(triangle)
                break
    return wrong_triangles


def find_adjacent_triangles(triangles):
    """
    Функция находит все пары треугольников из массива triangles, которые имеют общее ребро.
    Возвращает список кортежей, каждый из которых содержит два треугольника с общим ребром.
    """
    adjacent_triangles = []
    for i in range(len(triangles)):
        for j in range(i+1, len(triangles)):
            shared_vertices = set(triangles[i]).intersection(set(triangles[j]))
            if len(shared_vertices) == 2:
                adjacent_triangles.append((triangles[i], triangles[j]))
    return adjacent_triangles


def find_shared_edge(triangles):
    # создаем словарь для хранения количества вхождений каждой точки в треугольники
    point_counts = {}
    for triangle in triangles:
        for point in triangle:
            if point not in point_counts:
                point_counts[point] = 0
            point_counts[point] += 1

    # создаем множество для хранения точек, которые встречаются два раза в треугольниках
    shared_points = set(point for point, count in point_counts.items() if count == 2)

    # проходим по каждой паре треугольников и находим общие вершины
    common_vertices = []
    for i, triangle1 in enumerate(triangles):
        for j, triangle2 in enumerate(triangles):
            if i < j:
                vertices = set(point for point in triangle1 if point in triangle2 and point in shared_points)
                if len(vertices) == 2:
                    common_vertices.extend(list(vertices))

    # если найдено общее ребро между треугольниками, возвращаем координаты его вершин
    if len(common_vertices) == 2:
        return common_vertices

    # иначе возвращаем None
    return None


def find_unique_points(triangles):
    # создаем список для хранения всех точек
    points = []

    # проходим по каждому треугольнику и добавляем все его вершины в список точек
    for triangle in triangles:
        for point in triangle:
            points.append(point)

    # создаем множество для хранения повторяющихся точек
    duplicates = set()

    # проходим по каждой точке из списка и проверяем, есть ли такая точка в списке еще раз
    for point in points:
        if points.count(point) > 1:
            duplicates.add(point)

    # проходим по каждому треугольнику и находим две вершины, которые не повторяются в других треугольниках
    result_points = []
    for triangle in triangles:
        for point in triangle:
            if point not in duplicates and len(result_points) < 2:
                result_points.append(point)

    # возвращаем результат в виде списка
    return result_points


def edges_tuple(edges):
    new_edges = []
    for edge in edges:
        new_edges.append(sorted((tuple(edge[0]), tuple(edge[1]))))
    return new_edges


def flip(wrong_triangles, edges):
    new_edges = edges
    pairs = find_adjacent_triangles(wrong_triangles)
    for pair in pairs:
        bad = sorted(find_shared_edge(pair))
        good = sorted(find_unique_points(pair))
        if bad in new_edges:
            new_edges.remove(bad)
        new_edges.append(good)
    return new_edges