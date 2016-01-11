# This class describes a FullGesture, which keeps track of all iterations of a gesture, rather than an average.
# These iterations are used to maintain a running average of the gesture, to allow it to change with time.
# Each FullGesture is associated with exactly one LearnedGesture object.

from GestureCreator import GestureCreator


# TODO Add functionality to keep gesture profile updated, with a certain chance of including iteration in the average.
# TODO Discount past iterations' chance of being included.
class FullGesture:

    def __init__(self, name, gesture_iterations, gesture):
        self.gesture_iterations = gesture_iterations  # The array of gesture iterations.
        self.name = name  # Name of the gesture.
        self.full_gesture = (name, gesture_iterations)
        # TODO update this to use a parameter for full gestures file when fully implemented
        self.gesture_creator = GestureCreator('full_gestures.txt')
        self.gesture = gesture

    # Appends a new iteration of a gesture to the end of the current list of iterations.
    def append_iteration(self, iteration):
        self.gesture_iterations.append(iteration)

    # Use particle filtering to decide which iterations should be included in the average.
    # Older iterations have a smaller chance of being included.
    def sample_average(self):
        # TODO implement functionality to average a gesture based on probability.
        average = self.gesture_creator.average_gesture(self.gesture_iterations)
        return average

    def get_name(self):
        return self.name

    def get_gesture_iterations(self):
        return self.gesture_iterations

    def get_gesture(self):
        return self.full_gesture
