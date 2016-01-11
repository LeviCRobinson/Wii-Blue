# A class defining a learned gesture for BlueMote.
# A LearnedGesture is one that is stored on the system.
import subprocess

class LearnedGesture:

    def __init__(self, name, frames, action, attempts, successes, iterations):
        self.frames = frames # Readings defining the gesture
        self.name = name  # Human readable name for identification.
        self.action = action  # The action to be taken when this gesture is performed.
        self.attempts = attempts       # The number of times this gesture was recognized.
        self.successes = successes      # The number of times this gesture was successfully attempted.
        self.iterations = iterations # Past frames of iterations of the gesture.
        self.gesture = (self.name, self.frames, self.action, self.attempts, self.successes, self.iterations)

    # Returns the roll at the given frame index.
    def get_roll(self, index):
        if index >= len(self.frames):
            print "LearnedGesture.get_roll: Error.  Index out of bounds."
            return
        return self.frames[index][0]

    # Returns the pitch at the given frame index.
    def get_pitch(self, index):
        if index >= len(self.frames):
            print "LearnedGesture.get_pitch: Error.  Index out of bounds."
            return
        return self.frames[index][1]

    # Returns the x coordinate at the given frame index.
    def get_X(self, index):
        if index >= len(self.frames):
            print "LearnedGesture.get_x: Error.  Index out of bounds."
            return
        return self.frames[index][2]

    # Returns the y coordinate at the given frame index.
    def get_Y(self, index):
        if index >= len(self.frames):
            print "LearnedGesture.get_y: Error.  Index out of bounds."
            return
        return self.frames[index][3]

    # Returns the z coordinate at the given frame index.
    def get_Z(self, index):
        if index >= len(self.frames):
            print "LearnedGesture.get_z: Error.  Index out of bounds."
            return
        return self.frames[index][4]

    # Returns the name of the gesture.
    def get_name(self):
        return self.name

    # Returns the action associated with the gesture.
    def get_action(self):
        return self.action

    # Returns the length of the gesture, in frames.
    def get_length(self):
        return len(self.frames)

    # Returns a full frame
    def get_frame(self, index):
        if index >= len(self.frames):
            print "LearnedGesture.get_frame: Error.  Index out of bounds."
            return
        return self.frames[index]

    # Returns the full list of frames representing the gesture.
    def get_frames(self):
        return self.frames

    def get_iterations(self):
        return self.iterations

    # Returns the tuple that contains the gesture name and frames.
    def get_gesture(self):
        return self.gesture

    # Sets the action for this gesture.
    def set_action(self, action):
        self.action = action
        self.gesture = (self.name, self.frames, self.action, self.attempts, self.successes, self.iterations)

    # Calls the action assigned with this Gesture.
    def call_action(self):
        if self.action == ['None'] or self.action == []:
            return
        else:
            subprocess.Popen(self.action)

    # Increments the amount of attempts for this gesture
    def incr_attempts(self):
        self.attempts += 1
        self.gesture = (self.name, self.frames, self.action, self.attempts, self.successes, self.iterations)

    # Increments the amount of successes for this gesture
    def incr_successes(self):
        self.successes += 1
        self.gesture = (self.name, self.frames, self.action, self.attempts, self.successes, self.iterations)

    # Sets the number of attempts to num_attempts for this gesture
    def set_attempts(self, num_attempts):
        self.attempts = num_attempts
        self.gesture = (self.name, self.frames, self.action, self.attempts, self.successes, self.iterations)

    # Sets the number of successes to num_successes for this gesture.
    def set_successes(self, num_successes):
        self.successes = num_successes
        self.gesture = (self.name, self.frames, self.action, self.attempts, self.successes, self.iterations)

    def reset_stats(self):
        self.set_attempts(0)
        self.set_successes(0)
        self.gesture = (self.name, self.frames, self.action, self.attempts, self.successes, self.iterations)

    def get_attempts(self):
        return self.attempts

    def get_successes(self):
        return self.successes

    # Appends an array of frames to the list of iterations, up to 20.
    # removes first iteration at 20th iteration.
    def append_iteration(self, frames):
        # If 20 iterations in the list, remove the first
        if len(self.iterations) >= 10:
            self.iterations.pop(0)
        # Append the new frames to the end of the list.
        self.iterations.append(frames)

    # Takes iterations of a gesture, and averages them frame-by-frame.
    # i.e., average first frame readings, average second frame readings, etc.
    def average_gesture(self):
        min_length = float('inf')

        # Find the shortest of the gestures for indexing purposes.
        for frames in self.iterations:
            if len(frames) < min_length:
                min_length = len(frames)

        if min_length == 0:
            print "Error:  A gesture had no length.  Exiting."
            exit(1)

        avg_frames = []

        for i in range(0, min_length):
            roll_sum = 0.0
            pitch_sum = 0.0
            acc_x_sum = 0.0
            acc_y_sum = 0.0
            acc_z_sum = 0.0
            for j in range (0, len(self.iterations)):
                # Sum the sensor readings at t = i
                roll_sum += self.iterations[j][i][0]   # Roll reading for this frame
                pitch_sum += self.iterations[j][i][1]  # Pitch reading for this frame
                acc_x_sum += self.iterations[j][i][2]  # X accelerometer
                acc_y_sum += self.iterations[j][i][3]  # Y accelerometer
                acc_z_sum += self.iterations[j][i][4]  # Z accelerometer

            # Append the average of each of these to the gesture average.
            avg_frames.append( (roll_sum/len(self.iterations),
                               pitch_sum/len(self.iterations),
                               acc_x_sum/len(self.iterations),
                               acc_y_sum/len(self.iterations),
                               acc_z_sum/len(self.iterations) ))

        # Return the point-by-point average of the frames.
        return avg_frames

    #
    def update_and_average(self, frames):
        self.append_iteration(frames)
        self.frames = self.average_gesture()