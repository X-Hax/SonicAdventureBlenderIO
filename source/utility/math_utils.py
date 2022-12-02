import math
from typing import Callable

from mathutils import Matrix, Euler, Quaternion


def get_normal_matrix(matrix: Matrix):
    return matrix.to_3x3().transposed().inverted()


def remove_deviations(
        frames: list[int],
        values: dict[int, any],
        start: int | None,
        end: int | None,
        deviation_threshold: float,
        lerp: Callable[[any, any, float], any],
        calculate_deviation: Callable[[any, any], float]):

    if start is None:
        start = frames[0]
        from_index = 1
    else:
        from_index = frames.index(start) + 1

    if end is None:
        end = frames[-1]
        to_index = len(frames) - 1
    else:
        to_index = frames.index(end)

    if end - start < 2 or deviation_threshold <= 0:
        return

    # basically: whenever we remove a frame, we want to ignore the second
    # one so that we can check it in the next iteration.
    # we are done as soon as we get an iteration
    # in which no frame was removed

    done = False
    while not done:
        done = True

        i = from_index
        while i < to_index:
            previous = frames[i - 1]
            current = frames[i]
            next = frames[i + 1]

            linear_fac = (current - previous) / (next - previous)

            linear = lerp(values[previous], values[next], linear_fac)
            actual = values[current]

            deviation = calculate_deviation(linear, actual)
            if deviation < deviation_threshold:
                del frames[i]
                to_index -= 1
                done = False

            i += 1


def lerp_quaternion(a: Quaternion, b: Quaternion, t: float):
    t1 = 1 - t
    return Quaternion((
        a.w * t1 + b.w * t,
        a.x * t1 + b.x * t,
        a.y * t1 + b.y * t,
        a.z * t1 + b.z * t
    ))


def calc_quaternion_deviation(a: Quaternion, b: Quaternion):
    return math.sqrt(
        (a.x - b.x)**2
        + (a.y - b.y)**2
        + (a.z - b.z)**2
        + (a.w - b.w)**2
    )


def lerp_euler(a: Euler, b: Euler, t: float):
    t1 = 1 - t
    return Euler((
        a.x * t1 + b.x * t,
        a.y * t1 + b.y * t,
        a.z * t1 + b.z * t
    ))


def calc_euler_deviation(a: Euler, b: Euler):
    return math.degrees(math.sqrt(
        (a.x - b.x)**2
        + (a.y - b.y)**2
        + (a.z - b.z)**2
    ))
