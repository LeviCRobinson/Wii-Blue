# This class defines a GestureCreator, which performs tasks necessary to learning and maintaining gestures.
from PerformedGesture import PerformedGesture
from LearnedGesture import LearnedGesture
from WriterReader import GestureWriterReader
import shlex, wiiuse



class GestureCreator:

    def __init__(self, gestures_file, wiimotes, first_wm, num_motes, frame_freq):
        self.writer_reader = GestureWriterReader(gestures_file)
        self.wiimotes = wiimotes
        self.first_wm = first_wm
        self.num_motes = num_motes
        self.frame_freq = frame_freq
        self.known_gestures = self.writer_reader.get_learned_gestures()
        # self.full_gestures = self.writer_reader.get_full_gestures()

    # Takes iterations of a gesture, and averages them frame-by-frame.
    def average_gesture(self, frame_arr):
        min_length = float('inf')

        # Find the shortest of the gestures for indexing purposes.
        for frames in frame_arr:
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
            for j in range (0, len(frame_arr)):
                roll_sum += frame_arr[j][i][0]   # Roll reading for this frame
                pitch_sum += frame_arr[j][i][1]  # Pitch reading for this frame
                acc_x_sum += frame_arr[j][i][2]  # X accelerometer
                acc_y_sum += frame_arr[j][i][3]  # Y accelerometer
                acc_z_sum += frame_arr[j][i][4]  # Z accelerometer
            avg_frames.append((roll_sum/len(frame_arr), pitch_sum/len(frame_arr), acc_x_sum/len(frame_arr),
                               acc_y_sum/len(frame_arr), acc_z_sum/len(frame_arr)))

        return avg_frames

    # Prompts the user to go through the process of learning a gesture,
    # (Repeating the gesture several times, averaging these repetitions,
    # and writing this average to the gestures.txt file.)
    # rep_limit:  The number of repetitions to learn the gesture.
    def learn_gesture(self, rep_limit):

        repetitions = 0         # How many times a gesture has been repeated.
        done = False
        confirmed = False

        while not confirmed:
            gest_name = raw_input("Please name your gesture: ")

            if not (self.get_gesture_names().__contains__(gest_name) or
                    len(gest_name) > 15):
                confirmed = True
            else:
                print "\nGesture name taken or too long.  Please choose another.\n"
        gest_action = raw_input("Please specify an command for your gesture: ")

        gest_arg_arr = shlex.split(gest_action)
        frame_arr = []

        print "\nPress and hold B, perform your gesture, and then release B."

        i = 0
        while not done:
            r = wiiuse.poll(self.wiimotes, self.num_motes)
            if r != 0:

                if wiiuse.is_just_pressed(self.first_wm[0], wiiuse.button['B']):
                    print "Learning gesture, round " + str(repetitions+1) + "."

                    frames = []

                if wiiuse.is_held(self.first_wm[0], wiiuse.button['B']):
                    roll = self.first_wm[0].orient.roll
                    pitch = self.first_wm[0].orient.pitch
                    acc_x = self.first_wm[0].gforce.x
                    acc_y = self.first_wm[0].gforce.y
                    acc_z = self.first_wm[0].gforce.z

                    frame = (roll, pitch, acc_x, acc_y, acc_z)

                    # Only add every nth frame to the list.
                    if i%self.frame_freq == 0:
                        frames.append(frame)

                if repetitions >= rep_limit:
                    done = True
                    print "Good! Press A to see your gesture added to the list of known gestures."
                    continue

                if wiiuse.is_released(self.first_wm[0], wiiuse.button['B']):
                    repetitions += 1
                    frame_arr.append(frames)
                    print str(rep_limit-repetitions) + " repetition(s) remaining."

                i += 1

        # Creating the average of the repetitions to create the learned gesture.
        gesture_average = self.average_gesture(frame_arr)

        # Writing Gesture to the gesture file.
        gesture = LearnedGesture(gest_name, gesture_average, gest_arg_arr, 0, 0, frame_arr)
        self.writer_reader.write_gesture(gesture)

        # Update the current known gestures.
        self.update_gestures()

    # Collects the data of a gesture to be compared to known gestures.
    def perform_gesture(self):
        done = False

        if len(self.known_gestures) == 0:
            return
        i = 0
        frames = []
        while not done:
            r = wiiuse.poll(self.wiimotes, self.num_motes)
            if r != 0:

                if wiiuse.is_held(self.first_wm[0], wiiuse.button['B']):
                    roll = self.first_wm[0].orient.roll
                    pitch = self.first_wm[0].orient.pitch
                    acc_x = self.first_wm[0].gforce.x
                    acc_y = self.first_wm[0].gforce.y
                    acc_z = self.first_wm[0].gforce.z

                    frame = (roll, pitch, acc_x, acc_y, acc_z)

                    # Only add every nth frame to the list.
                    if i % self.frame_freq == 0:
                        frames.append(frame)

                if wiiuse.is_released(self.first_wm[0], wiiuse.button['B']):
                    done = True
                i += 1

        gesture = PerformedGesture(frames)
        return gesture

    def update_gestures(self):
        self.known_gestures = self.writer_reader.get_learned_gestures()
        # self.full_gestures = self.writer_reader.get_full_gestures()

    def get_gesture_names(self):
        names = []
        for g in self.known_gestures:
            names.append(g.get_name())

        return names
