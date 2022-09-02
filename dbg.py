import matplotlib.pyplot as plt
import numpy as np

from library.Math import rotation_matrix, create_corners, calc_location


def calc_theta_ray(width, box_2d, proj_matrix):
    """
    Calculate global angle of object, see paper
    """
    # Angle of View: fovx (rad) => 3.14
    fovx = 2 * np.arctan(width / (2 * proj_matrix[0][0]))
    center = (box_2d[1][0] + box_2d[0][0]) / 2
    dx = center - proj_matrix[0][2]

    mult = 1
    if dx < 0:
        mult = -1
    dx = abs(dx)
    angle = np.arctan((2 * dx * np.tan(fovx / 2)) / width)
    angle = angle * mult

    return angle


def draw_lines(ax, x, y, idx, color='C0'):
    for i0, i1 in idx:
        ax.plot([x[i0], x[i1]], [y[i0], y[i1]], color=color)


def draw_on_bev(ax, x, z, color1='C0', color2='C3'):
    draw_lines(ax, x, z, [(0, 1), (5, 4), (4, 0)], color1)
    draw_lines(ax, x, z, [(1, 5)], color2)
    ax.grid(True)
    ax.axis('equal')
    ax.set_ylim([0, 30])
    ax.set_xlim([-20, 20])


def draw_on_image(ax, u, v, color1='C0', color2='C3'):
    draw_lines(ax, u, v, [(0, 1), (5, 4), (4, 0), (7, 6), (6, 2), (2, 3),
                          (2, 0), (6, 4)], color1)
    draw_lines(ax, u, v, [(1, 5), (5, 7), (7, 3), (3, 1)], color2)
    ax.grid(True)
    ax.set_ylim(1.25, -1.25)
    ax.set_xlim(-1.25, 1.25)


def f(width, length, height, x, y, z, theta):
    R = rotation_matrix(np.deg2rad(theta))
    corners = np.array(create_corners((height, length, width), (x, y, z), R))
    x, y, z = corners[:, 0], corners[:, 1], corners[:, 2]
    u = x / z
    v = y / z
    u0, u1 = u.min(), u.max()
    v0, v1 = v.min(), v.max()

    plt.figure(1, figsize=(12, 6))
    ax1 = plt.subplot(121)
    ax2 = plt.subplot(122)

    draw_on_bev(ax1, x, z, 'gray', 'black')
    draw_on_image(ax2, u, v, 'gray', 'black')

    # for i in range(8):
    #     ax2.text(u[i], v[i], str(i))

    P = np.eye(3, 4)
    box_2d = [(u0, v0), (u1, v1)]
    theta_ray = calc_theta_ray(1, box_2d, P)
    alpha = np.deg2rad(theta) - theta_ray

    location, X = calc_location((height, length, width), P, box_2d, alpha,
                                theta_ray)

    corners = np.array(create_corners((height, length, width), location, R))
    x, y, z = corners[:, 0], corners[:, 1], corners[:, 2]
    u = x / z
    v = y / z

    draw_on_bev(ax1, x, z)
    draw_on_image(ax2, u, v)

    draw_lines(ax2, [u0, u1, u1, u0], [v0, v0, v1, v1], [(0, 1), (1, 2),
                                                         (2, 3), (3, 0)], 'C1')
    X = np.array(X)
    X = (R @ X.T).T + location
    u = X[:, 0] / X[:, 2]
    v = X[:, 1] / X[:, 2]
    ax2.plot(u, v, 'o', color='C1')

    plt.show()
    print('theta_ray', np.rad2deg(theta_ray))
    print('alpha', np.rad2deg(alpha))
    print('location', location)


if __name__ == '__main__':
    f(width=2, length=5, height=1.5, x=0, y=1.5, z=10, theta=15)
    f(width=2, length=5, height=1.5, x=0, y=1.5, z=10, theta=1)
    f(width=2, length=5, height=1.5, x=-5.1, y=0, z=8.25, theta=158.4)