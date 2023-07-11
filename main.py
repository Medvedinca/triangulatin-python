import os
import numpy as np
import matplotlib.pyplot as plt
import triangulation as tri


if os.path.exists("points.png") and os.path.exists("badtriangles.png") and \
        os.path.exists("badtricirc.png") and os.path.exists("good.png"):
    os.remove("points.png")
    os.remove("badtriangles.png")
    os.remove("badtricirc.png")
    os.remove("good.png")


# Создание случайных точек на плоскости
width = 50
height = 50
pointNumber = 10
points = np.zeros((pointNumber, 2))
points[:, 0] = np.random.randint(0, width, pointNumber)
points[:, 1] = np.random.randint(0, height, pointNumber)


# Вывод и сохранение точек
fig = plt.figure(figsize=(12, 8))
ax = plt.subplot()
plt.axis("equal")
ax.axis('equal')
plt.xlim(-20, 70)
plt.ylim(-20, 70)
plt.tight_layout()
ax.scatter(points[:, 0], points[:, 1], color='red')
plt.savefig('points.png')


# Строим жадную триангуляцию
segments = tri.get_lines(points)
greed = tri.greed(segments)


# Рисуем жадную триангуляцию
for segment in greed:
    x1, y1 = segment[0][0], segment[0][1]
    x2, y2 = segment[1][0], segment[1][1]
    plt.plot([x1, x2], [y1, y2], 'b-', alpha=0.3)
plt.savefig('badtriangles.png')


# Ищем все возможные треугольники и треугольники которые не удовлетваряют Делоне
triangles = tri.find_triangles(greed, points)
wrong_triangles = tri.check_delaunay(triangles, points)


# Ищем окружности неправильных треугольников и отрисовываем
circles = tri.get_circles(wrong_triangles)
for i in range(len(circles)):
    if circles is not None:
        circle = plt.Circle((circles[i][0], circles[i][1]), circles[i][2], fill=False, alpha=0.3)
        ax.add_patch(circle)


# Сохраняем информацию в файл
tri.create_json(points, triangles, wrong_triangles)


# Отрисовываем неправильные треугольники красным
for segment in wrong_triangles:
    x1, y1 = segment[0][0], segment[0][1]
    x2, y2 = segment[1][0], segment[1][1]
    x3, y3 = segment[2][0], segment[2][1]
    plt.plot([x1, x2], [y1, y2], 'r-', alpha=0.3)
    plt.plot([x2, x3], [y2, y3], 'r-', alpha=0.3)
    plt.plot([x3, x1], [y3, y1], 'r-', alpha=0.3)
plt.savefig('badtricirc.png')


# Очищаем график и рисуем неправильную триангуляцию
plt.clf()
plt.axis("equal")
ax.axis('equal')
plt.xlim(-20, 70)
plt.ylim(-20, 70)
plt.tight_layout()
for segment in greed:
    x1, y1 = segment[0][0], segment[0][1]
    x2, y2 = segment[1][0], segment[1][1]
    plt.plot([x1, x2], [y1, y2], 'b-', alpha=0.3)


# Преобразуем рёбра в кортеж
edges = tri.edges_tuple(segments)


# Проверка делоне в цикле до отсутствия вронгов или итераций
iteration = 0
new_triangles = tri.greed(edges)
while True:
    if len(wrong_triangles) == 0 or iteration == 5:
        for segment in new_triangles:
            x1, y1 = segment[0][0], segment[0][1]
            x2, y2 = segment[1][0], segment[1][1]
            plt.plot([x1, x2], [y1, y2], color="black", alpha=1)
        break
    else:
        edges = tri.flip(wrong_triangles, edges)
        new_triangles = tri.greed(edges)
        triangles = tri.find_triangles(new_triangles, points)
        wrong_triangles = tri.check_delaunay(triangles, points)
        iteration = iteration+1

plt.savefig('good.png')