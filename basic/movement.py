import math


def ease_in_out_cubic_scaled(x):
    t = (x - 0) / (1 - 0)  # normalize x from [0, 1]
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 3) / 2


def ease_out_quad(t):
    return 1 - (1 - t) ** 2


def smoothstep(t):
    return t * t * (3 - 2 * t)


def cubic_bezier(t, p0, p1, p2, p3):
    """Evaluate cubic Bezier at t in [0,1]"""
    return (
        (1 - t)**3 * p0 +
        3 * (1 - t)**2 * t * p1 +
        3 * (1 - t) * t**2 * p2 +
        t**3 * p3
    )


def cubic_bezier_derivative(t, p0, p1, p2, p3):
    """Derivative of cubic Bezier curve at t"""
    return (
        3 * (1 - t)**2 * (p1 - p0) +
        6 * (1 - t) * t * (p2 - p1) +
        3 * t**2 * (p3 - p2)
    )


def solve_cubic_bezier_x(t, x1, x2, epsilon=1e-6):
    """Find parameter u so that cubic Bezier x(u) = t by Newton-Raphson"""
    u = t  # initial guess

    for _ in range(20):
        x = cubic_bezier(u, 0, x1, x2, 1)
        dx = cubic_bezier_derivative(u, 0, x1, x2, 1)
        if abs(x - t) < epsilon:
            return u
        if dx == 0:
            break
        u = u - (x - t) / dx
        if u < 0:
            u = 0
        elif u > 1:
            u = 1
    return u


def cubic_bezier_ease(t, x1, y1, x2, y2):
    """True cubic Bezier easing function"""
    u = solve_cubic_bezier_x(t, x1, x2)
    y = cubic_bezier(u, 0, y1, y2, 1)
    return y


# Example Windows 11–like easing control points:
# Control points taken from common UI curve: (0.33, 0, 0.67, 1)
def windows11_cubic_bezier(t):
    return cubic_bezier_ease(t, 0.1, 0.9, 0.2, 1)


def ease_out_elastic(t):
    c4 = (2 * math.pi) / 3

    if t == 0:
        return 0
    if t == 1:
        return 1

    return pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1


def ease_in_out_elastic(t):
    c5 = (2 * math.pi) / 4.5

    if t == 0:
        return 0
    if t == 1:
        return 1
    if t < 0.5:
        return -(pow(2, 20 * t - 10) * math.sin((20 * t - 11.125) * c5)) / 2
    else:
        return pow(2, -20 * t + 10) * math.sin((20 * t - 11.125) * c5) / 2 + 1


def ease_out_elastic_gentle(t):
    c4 = (2 * math.pi) / 4.5  # moderate oscillation speed
    decay = 9  # decay tuned for quick settling

    if t == 0:
        return 0
    if t == 1:
        return 1

    return pow(2, -decay * t) * math.sin((t * 10 - 0.75) * c4) + 1


def ease_in_out_cubic_bounce(x):
    t = x  # Already normalized [0, 1]
    if t < 0.5:
        return 4 * t * t * t
    else:
        overshoot = 1.15  # goes up to 115% then settles back to 100%
        t2 = (t - 0.5) * 2  # remap to [0, 1]
        cubic = 1 - pow(-2 * t + 2, 3) / 2
        bounce = (overshoot - 1) * math.sin((t2) * math.pi)
        return min(cubic + bounce * (1 - t2), overshoot)


def windows11_bounce_bezier(t):
    # Overshoot control: increase y2 beyond 1
    return cubic_bezier_ease(t, 0.3, 0.0, 0.6, 1.35)


def windows10_cubic_bezier(t):
    return cubic_bezier_ease(t, 0.4, 0.0, 0.2, 1.0)


def g_moving_in(t):
    return cubic_bezier_ease(t, 0.0, 0.0, 0.2, 1.0)


def g_moving_out(t):
    return cubic_bezier_ease(t, 0.4, 0.0, 1.0, 1.0)


def g_default(t):
    return cubic_bezier_ease(t, 0.4, 0.0, 0.2, 1)
