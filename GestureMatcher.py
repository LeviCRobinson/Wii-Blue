# This class performs the gesture recognition for BlueMote

import wiiuse
import math
from LearnedGesture import LearnedGesture
from PerformedGesture import PerformedGesture
import operator


class GestureMatcher:

    def __init__(self, writer_reader):
        self.writer_reader = writer_reader
        self.known_gestures = self.writer_reader.get_learned_gestures()
        self.SENSOR_MAX_ROLL = 180
        self.SENSOR_MAX_PITCH = 180
        self.SENSOR_MAX_ACC_X = 26
        self.SENSOR_MAX_ACC_Y = 26
        self.SENSOR_MAX_ACC_Z = 26

    # Returns a gesture based on which has the smallest variance from the given gesture.
    # Fast, but adds the variances of all sensor readings together indiscriminately,
    # Which may not be entirely representative of the gesture.
    def variance_recognition(self, gesture):
        all_gestures_variances = []

        for g in self.known_gestures:
            total_roll_variance = 0.0
            total_pitch_variance = 0.0
            total_x_variance = 0.0
            total_y_variance = 0.0
            total_z_variance = 0.0

            # Use length of the shorter gesture to avoid indexing errors.
            shorter_gesture_length = min(gesture.get_length(), g.get_length())

            for i in range(0, shorter_gesture_length): # From 0 to the length of the shorter gesture.
                total_roll_variance += (gesture.get_roll(i)-g.get_roll(i))**2
                total_pitch_variance += (gesture.get_pitch(i)-g.get_pitch(i))**2
                total_x_variance += (gesture.get_X(i)-g.get_X(i))**2
                total_y_variance += (gesture.get_Y(i)-g.get_Y(i))**2
                total_z_variance += (gesture.get_Z(i)-g.get_Z(i))**2
                # frame_variances = (roll_variance, pitch_variance, x_variance, y_variance, z_variance)
                # gesture_variances.append(frame_variances)

            total_gesture_variances = (total_roll_variance, total_pitch_variance, total_x_variance,
                                       total_y_variance, total_z_variance)

            # Store the gesture name and its total variances from the performed gesture.
            all_gestures_variances.append((g.get_name(), total_gesture_variances))

        # Find the gesture with the lowest variance from the performed gesture.
        compound_gesture_variances = []
        for v in all_gestures_variances:
            # Append gesture name, and its standard deviation from the performed gesture
            compound_gesture_variances.append((v[0], math.sqrt(sum(v[1]))/shorter_gesture_length))
            # print "Average variance: ", v[0], math.sqrt(sum(v[1]))/shorter_gesture_length

        # Find gesture with the lowest variance.
        closest = min(compound_gesture_variances, key=lambda tup: tup[1])

        matched_gesture = self.get_gesture_from_name(closest[0])

        if matched_gesture is None:
            print "variance_recognition, Error: No matched gesture by name "+closest[0]

        return matched_gesture

    # Returns a gesture based on which has the greatest amount of closest sensor
    # readings to the performed gesture
    def greatest_closest_recognition(self, performed_gesture):
        weights = [1,1,1,1,1,1]
        weights = self.evaluation_function(performed_gesture)
        gesture_dict = {}
        length_differences = {}

        for g in self.known_gestures:
            # Initialize each gesture's closest reading count to 0.
            gesture_dict.update({g.get_name() : 0})

            # If the gesture is longer than the performed gesture, record its name
            # and penalize for the difference of their lengths (a gesture is guaranteed
            # not to be closest to nonexistent frames)
            if g.get_length() > performed_gesture.get_length():
                diff = g.get_length() - performed_gesture.get_length()
                gesture_dict[g.get_name()] -= diff

        closest_gesture_roll=None
        closest_gesture_pitch=None
        closest_gesture_X=None
        closest_gesture_Y=None
        closest_gesture_Z = None

        for i in range(0, len(performed_gesture.get_frames())):
            closest_gesture_roll = self.closest_roll(performed_gesture.get_frame(i), i)
            closest_gesture_pitch = self.closest_pitch(performed_gesture.get_frame(i), i)
            closest_gesture_X = self.closest_x(performed_gesture.get_frame(i), i)
            closest_gesture_Y = self.closest_y(performed_gesture.get_frame(i), i)
            closest_gesture_Z = self.closest_z(performed_gesture.get_frame(i), i)
            # closest_gesture_length = self.closest_length(performed_gesture)

            if closest_gesture_roll is not None:
                gesture_dict[closest_gesture_roll.get_name()] += 1*weights[0]
            if closest_gesture_pitch is not None:
                gesture_dict[closest_gesture_pitch.get_name()] += 1*weights[1]
            if closest_gesture_X is not None:
                gesture_dict[closest_gesture_X.get_name()] += 1*weights[2]
            if closest_gesture_Y is not None:
                gesture_dict[closest_gesture_Y.get_name()] += 1*weights[3]
            if closest_gesture_Z is not None:
                gesture_dict[closest_gesture_Z.get_name()] += 1*weights[4]
            # if closest_gesture_length is not None:
            #     gesture_dict[closest_gesture_length.get_name()] += 1

        # Return the gesture that has the greatest amount of closest frames
        name = max(gesture_dict.iteritems(), key=operator.itemgetter(1))[0]
        sorted_gesture_dict = sorted(gesture_dict.items(), key=operator.itemgetter(1))
        sorted_gesture_dict.reverse()
        return self.get_gesture_from_name(name)

    # An evaluation function that weights sensor readings based on how much they change within the gesture.
    # This allows prioritization of sensor readings in the model, and it allows us to assign less weight
    # to sensor readings that don't define the gesture, but that may be done accidentally.
    #  (E.g., X-accelerometer in an up-down gesture.)
    # Returns:  A list of weights for roll, pitch, X, Y, and Z sensor readings.
    def evaluation_function(self, performed_gesture):
        self_roll_var = self.self_variance_roll(performed_gesture)
        self_pitch_var = self.self_variance_pitch(performed_gesture)
        self_x_var = self.self_variance_x(performed_gesture)
        self_y_var = self.self_variance_y(performed_gesture)
        self_z_var = self.self_variance_z(performed_gesture)

        raw_variances_rp = [self_roll_var, self_pitch_var]
        raw_variances_acc = [self_x_var, self_y_var, self_z_var]
        if sum(raw_variances_rp) != 0:

            # Normalize Roll and pitch relative to each other
            normalized_variances_rp = [float(num)/sum(raw_variances_rp) for num in raw_variances_rp]
            # Normalize X,Y, and Z relative to each other.
            normalized_variances_acc = [float(num)/sum(raw_variances_acc) for num in raw_variances_acc]

            length_weight = 0.2
            normalized_variances_acc.append(length_weight)

            # Normalized values, in order:  Roll, pitch, x, y, z.
            weights = normalized_variances_rp + normalized_variances_acc

            return weights
        # Penalize being longer or shorter than the performed gesture.

    # Returns the gesture that has the lowest total variance from the given frame at time = index.
    # If index is out of range, moves on to the next gesture.
    def get_closest_gesture(self, frame, index):
        min_variance = float('inf')
        closest_gesture = None
        for g in self.known_gestures:

            if index > len(g.get_frames()):
                continue

            roll_variance = 0.0
            pitch_variance = 0.0
            x_variance = 0.0
            y_variance = 0.0
            z_variance = 0.0

            roll_variance += (frame[0]-g.get_roll(index))**2
            pitch_variance += (frame[1]-g.get_pitch(index))**2
            x_variance += (frame[2]-g.get_X(index))**2
            y_variance += (frame[3]-g.get_Y(index))**2
            z_variance += (frame[4]-g.get_Z(index))**2
            frame_variances = (roll_variance, pitch_variance, x_variance, y_variance, z_variance)

            # The sum of all of the variances in the frame.
            total_variance = sum(frame_variances)
            # print "get_closest_gesture: ", g, total_variance
            if total_variance < min_variance:
                closest_gesture = g
                min_variance = total_variance

        return closest_gesture

    # Returns the gesture that has the lowest roll variance from the given frame
    # at time = index
    def closest_roll(self, frame, index):
        min_variance = float('inf')
        closest_gesture = None
        for g in self.known_gestures:
            if index >= len(g.get_frames()):
                continue
            roll_variance = 0.0
            roll_variance += (frame[0]-g.get_roll(index))**2

            # If the roll variance of the current frame is less
            # than the current minimum, replace it
            if roll_variance < min_variance:
                closest_gesture = g
                min_variance = roll_variance

        return closest_gesture

    # Returns the gesture that has the lowest pitch variance from the given frame
    # at time = index
    def closest_pitch(self, frame, index):
        min_variance = float('inf')
        closest_gesture = None
        for g in self.known_gestures:
            if index >= len(g.get_frames()):
                continue
            pitch_variance = 0.0
            pitch_variance += (frame[1]-g.get_pitch(index))**2

            # Keep track minimum pitch variance
            if pitch_variance < min_variance:
                closest_gesture = g
                min_variance = pitch_variance

        return closest_gesture

    # Returns the gesture that has the lowest X-coordinate variance from the given frame
    # at time = index
    def closest_x(self, frame, index):
        min_variance = float('inf')
        closest_gesture = None
        for g in self.known_gestures:
            if index >= len(g.get_frames()):
                continue
            x_variance = 0.0
            x_variance += (frame[2]-g.get_X(index))**2

            # Keep track of minimum x variance
            if x_variance < min_variance:
                closest_gesture = g
                min_variance = x_variance

        return closest_gesture

    # Returns the gesture that has the lowest Y-coordinate variance from the given frame
    # at time = index
    def closest_y(self, frame, index):
        min_variance = float('inf')
        closest_gesture = None
        for g in self.known_gestures:
            if index >= len(g.get_frames()):
                continue
            y_variance = 0.0
            y_variance += (frame[3]-g.get_Y(index))**2

            # Keep track of minimum x variance
            if y_variance < min_variance:
                closest_gesture = g
                min_variance = y_variance

        return closest_gesture

    # Returns the gesture that has the lowest Y-coordinate variance from the given frame
    # at time = index
    def closest_z(self, frame, index):
        min_variance = float('inf')
        closest_gesture = None

        for g in self.known_gestures:
            if index >= len(g.get_frames()):
                continue
            z_variance = 0.0
            z_variance += (frame[4]-g.get_Z(index))**2

            # Keep track of minimum x variance
            if z_variance < min_variance:
                closest_gesture = g
                min_variance = z_variance

        return closest_gesture

    def closest_length(self, gesture):
        closest_gesture = None
        min_difference = float('inf')
        for g in self.known_gestures:
            if abs(len(g.get_frames())-len(gesture.get_frames())) < min_difference:
                min_difference = abs(len(g.get_frames())-len(gesture.get_frames()))
                closest_gesture = g

        return closest_gesture

    # Returns the total variation of roll within a single gesture.
    # Used to determine how much the roll sensor reading is changing over time.
    @staticmethod
    def self_variance_roll(gesture):
        total_roll_variance = 0
        for i in range(0, gesture.get_length()-1):
            total_roll_variance += (gesture.get_roll(i)-gesture.get_roll(i+1))**2

        return total_roll_variance

    # Returns the total variation of pitch within a single gesture.
    # Used to determine how much the pitch sensor reading is changing over time.
    @staticmethod
    def self_variance_pitch(gesture):
        total_pitch_variance = 0
        for i in range(0, gesture.get_length()-1):
            total_pitch_variance += (gesture.get_pitch(i)-gesture.get_pitch(i+1))**2

        return total_pitch_variance

    # Returns the total variation of x accelerometer within a single gesture.
    # Used to determine how much the x accelerometer reading is changing over time.
    @staticmethod
    def self_variance_x(gesture):
        total_x_variance = 0
        for i in range(0, gesture.get_length()-1):
            total_x_variance += (gesture.get_X(i)-gesture.get_X(i+1))**2

        return total_x_variance

    # Returns the total variation of y accelerometer within a single gesture.
    # Used to determine how much the y accelerometer reading is changing over time.
    @staticmethod
    def self_variance_y(gesture):
        total_y_variance = 0
        for i in range(0, gesture.get_length()-1):
            total_y_variance += (gesture.get_Y(i)-gesture.get_Y(i+1))**2

        return total_y_variance

    # Returns the total variation of z accelerometer within a single gesture.
    # Used to determine how much the z accelerometer  reading is changing over time.
    @staticmethod
    def self_variance_z(gesture):
        total_z_variance = 0
        for i in range(0, gesture.get_length()-1):
            total_z_variance += (gesture.get_Z(i)-gesture.get_Z(i+1))**2

        return total_z_variance

    def sensor_update(self):
        print "update sensor."

        # (Alpha)*P(e_t+1 | X_t+1)

    def transition_model_update(self):

        print "Update transition model based on which gesture was closest last."
        # SUM_x_t P(X_t+1 | x_t)*P(x_t | e_1:t)

    # Returns a gesture based on the given name.  If no matched gesture, return None.
    def get_gesture_from_name(self, g_name):

        for g in self.known_gestures:
            if g_name == g.get_name():
                return g

        return None

    # Updates the known gestures from the gestures file.
    def update_known_gestures(self):
        self.known_gestures = self.writer_reader.get_learned_gestures()
