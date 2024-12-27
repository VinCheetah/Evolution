"""
Define the RaceCarEvaluator
"""

import numpy as np
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt
from evopy.evaluator.neural_network.base import NNEvaluator


class RaceCarEvaluator(NNEvaluator):
    """ 
    This is the RacecarEvaluator
    """

    NNEvaluator.set_component_type("RaceCar")

    def __init__(self, options, **kwargs):
        options.ascending_order = False
        options.input_size = 5
        options.output_size = 6
        options.update(kwargs)
        circuit_opts = options.circuit_options
        NNEvaluator.__init__(self, options)

        self._circuit: Circuit = Circuit(circuit_opts.control_points, circuit_opts.track_width)

    def _evaluate(self, individual) -> float:
        return 0.

    def _compute_x(self, individual):
        # Compute the distance between the car and the track at different angle
        distances = np.zeros(self._input_size)
        for i in range(self._input_size):
            #
            distances[i] = self._circuit.distance_to_track(individual.x, individual.y, angle)
        return distances

    def plot(self, ax, individual) -> None:
        axs = self.get_subaxs(ax)
        ax1, ax2 = axs[0][0], axs[1][0]
        NNEvaluator.plot(self, ax1, individual)
        self._circuit.plot_circuit(ax2)

    def init_plot(self, ax) -> None:
        ax.clear()
        axs = self.create_subplots(ax, 2, 1)
        ax1, ax2 = axs[0][0], axs[1][0]
        NNEvaluator.init_plot(self, ax1)
        self._circuit.init_plot(ax2)


class Car:

    def __init__(self, circuit, options):
        self._circuit = circuit
        self.x = options.x
        self.y = options.y
        self.angle = options.angle
        self.speed = 0
        self.rotation_speed = options.rotation_speed
        self.max_speed = options.max_speed
        self.max_steering = options.max_steering


    def update_rotation(self, steering):
        self.angle += self.rotation_speed * steering
        self.angle = np.clip(self.angle, -np.pi / 4, np.pi / 4)

    def update_speed(self, throttle):
        self.speed += throttle
        self.speed = np.clip(self.speed, 0, self.max_speed)

    def update(self, dt, throttle, steering):
        # Update the car's position and angle based on the inputs
        self.angle += self.speed * np.tan(steering) / self.circuit.track_width * dt
        self.angle = np.clip(self.angle, -np.pi / 4, np.pi / 4)
        self.x += self.speed * np.cos(self.angle) * dt
        self.y += self.speed * np.sin(self.angle) * dt
        self.speed += throttle * dt
        self.speed = np.clip(self.speed, 0, 1)

        # Check if the car is off the track
        left_y = self.circuit.left_spline(self.x)
        right_y = self.circuit.right_spline(self.x)
        center_y = self.circuit.center_spline(self.x)
        if self.y < left_y or self.y > right_y:
            self.speed = 0
            self.x = self.x - self.speed * np.cos(self.angle) * dt
            self.y = self.y - self.speed * np.sin(self.angle) * dt
            self.angle = -self.angle
        return self.x, self.y, self.speed, self.angle


class Circuit:
    def __init__(self, control_points, track_width=10):
        self.track_width = track_width
        self.control_points = np.array(control_points)
        self.center_spline = self._create_spline(self.control_points)
        self.left_spline, self.right_spline = self._create_track_edges()

    def _create_spline(self, points):
        x = points[:, 0]
        y = points[:, 1]
        return CubicSpline(x, y)

    def _create_track_edges(self):
        """Generate the left and right edges of the track based on the center line spline."""
        # Sample points along the spline
        t_values = np.linspace(self.control_points[0, 0], self.control_points[-1, 0], 500)
        x_center = t_values
        y_center = self.center_spline(t_values)

        # Calculate tangents and normals for each point
        dx = np.gradient(x_center)
        dy = np.gradient(y_center)
        norm = np.sqrt(dx ** 2 + dy ** 2)
        dx /= norm
        dy /= norm

        # Calculate left and right track edges
        left_x = x_center - dy * self.track_width / 2
        left_y = y_center + dx * self.track_width / 2
        right_x = x_center + dy * self.track_width / 2
        right_y = y_center - dx * self.track_width / 2

        return (left_x, left_y), (right_x, right_y)

    def init_plot(self, ax):
        """Initialize the plot with the circuit."""
        ax.clear()
        self.plot_circuit(ax)

    def plot(self, ax, car):
        """Plot the circuit with the car's position."""
        # Plot the car which is a rectangle



    def plot_circuit(self, ax, cars=None):
        """Plot the circuit with center, left, and right track edges."""
        # Center track
        t_values = np.linspace(self.control_points[0, 0], self.control_points[-1, 0], 500)
        x_center = t_values
        y_center = self.center_spline(t_values)

        plt.plot(x_center, y_center, 'b-', label="Center line")
        plt.plot(*self.left_spline, 'r-', label="Left edge")
        plt.plot(*self.right_spline, 'g-', label="Right edge")
        plt.scatter(self.control_points[:, 0], self.control_points[:, 1], color='black', label="Control Points")

        plt.axis('equal')
        plt.legend()
        plt.show()

    def is_point_in_track(self, x, y):
        """Determine if a given point is within the track and return progress if inside."""
        t_values = np.linspace(self.control_points[0, 0], self.control_points[-1, 0], 500)
        x_center = t_values
        y_center = self.center_spline(t_values)

        distances = np.sqrt((x_center - x)**2 + (y_center - y)**2)
        closest_idx = np.argmin(distances)
        closest_dist = distances[closest_idx]

        # Check if within track width
        if closest_dist <= self.track_width / 2:
            progress = closest_idx / len(t_values)  # Percentage progress along the track
            return True, progress
        else:
            return False, None
