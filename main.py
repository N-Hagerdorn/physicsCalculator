# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import math
import numpy as np
from matplotlib import pyplot as plt

def go():
    print("Initial velocity (m/s): ")
    velocity_initial = int(input())

    print("Launch angle (degrees): ")
    angle = int(input())

    print("Launch platform height: ")
    height_initial = int(input())

    velocity_initial_x = velocity_initial * math.cos(angle * math.pi / 180.0)
    velocity_initial_y = velocity_initial * math.sin(angle * math.pi / 180.0)

    print("Initial x velocity is:", velocity_initial_x)
    print("Initial y velocity is:", velocity_initial_y)

    acceleration_x = 0
    acceleration_y = -9.8
    drag_coefficient = 0.42
    cross_sectional_area = 0.0032

    mass = 0.055

    # Find the maximum altitude of the object using kinetic energy to potential energy conversion
    vertical_kinetic_energy = 1/2 * mass * velocity_initial_y * velocity_initial_y
    maximum_potential_energy = -vertical_kinetic_energy
    altitude = maximum_potential_energy / (mass * acceleration_y)

    # Use mechanics to find the flight time to the peak of the flight
    rise_time = math.sqrt(abs(2 * altitude / acceleration_y))

    # Use mechanics to find the flight time from the peak of the flight to landing
    drop = altitude + height_initial
    fall_time = math.sqrt(abs(2 * drop / acceleration_y))


    flight_time = rise_time + fall_time

    t = np.linspace(0, flight_time, 100)

    '''
    plt.plot(t, f(t, 0, velocity_initial_x, acceleration_x), color='red')
    plt.show()

    plt.plot(t, f(t, height_initial, velocity_initial_y, acceleration_y), color='green')
    plt.show()
    '''

    plt.plot(f(t, 0, velocity_initial_x, acceleration_x), f(t, height_initial, velocity_initial_y, acceleration_y), color='green')
    plt.show()

def f(t, x0, v0, a):
    return x0 + v0 * t + 1/2 * a * t * t

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    go()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
