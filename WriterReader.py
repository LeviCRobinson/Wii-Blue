# This class describes an object that reads and writes to a gestures file,
# To maintain a list of Gesture objects that can be read from to recreate the Gestures.
# Note that no two Gestures may have the same name, by the GestureCreator object,
# in the LearnGesture method.

from ast import literal_eval
from LearnedGesture import LearnedGesture
import os


class GestureWriterReader:

    def __init__(self, gesture_file):
        self.gesture_file = gesture_file
        if not os.path.isfile(self.gesture_file):
            f = open(self.gesture_file, 'a')
            f.close()

    #  Writes a gesture to the gestures file.
    def write_gesture(self, gesture):
        f = open(self.gesture_file, 'a')  # Open gesture file for appending.
        str_gesture = str(gesture.get_gesture())
        f.write(str_gesture+"\n")
        f.close()

    #  Returns the gestures from the gestures.txt file. (Learned gestures.)
    def get_learned_gestures(self):
        f = open(self.gesture_file, 'r')
        known_gestures = []
        for line in f:
            gesture = line
            gesture = literal_eval(gesture)
            # Append a gesture with name, frames, action, attempts, successes, and iterations.
            known_gestures.append(LearnedGesture(gesture[0], gesture[1], gesture[2], gesture[3], gesture[4], gesture[5]))
        f.close()

        return known_gestures

    #  Deletes the contents of the gestures.txt file.
    def delete_gestures(self):
        f = open(self.gesture_file, 'w')
        f.seek(0)
        f.truncate()
        f.close()

    # Deletes a gesture by the name g_name.  Does not update currently known gestures.
    def delete_gesture(self, g_name):
        known_gestures = self.get_learned_gestures()

        # Make sure the gesture is actually known before trying to remove it.
        if self.get_gesture_from_name(g_name) is None:
            print "Delete_gesture: Gesture doesn't exist!"
            return

        for g in known_gestures:
            if g.get_name() == g_name:
                # Remove the gesture by the given name
                known_gestures.remove(g)

        # Format the file to contain nothing
        f = open(self.gesture_file, 'w')
        f.seek(0)
        f.truncate()
        f.close()

        # Write known gestures back to the file, without the named gesture.
        self.write_gestures(known_gestures)

    # Appends a list of gestures to the gestures file.
    def write_gestures(self, gestures):
        for g in gestures:
            self.write_gesture(g)

    # Overwrites the current gestures file to contain a new list of gestures.
    def overwrite_gestures(self, gestures):
        # Delete all gestures.
        self.delete_gestures()
        # Append a new list of gestures to the empty file.
        self.write_gestures(gestures)

    # Returns a list of gesture names currently known.
    def get_gesture_names(self):
        names = []
        for g in self.get_learned_gestures():
            names.append(g.get_name())

        return names

    def get_gesture_from_name(self, g_name):
        for g in self.get_learned_gestures():
            if g_name == g.get_name():
                return g

        return None

    def update_gesture(self, gesture):
        self.delete_gesture(gesture.get_name())
        self.write_gesture(gesture)

    # Prints all currently known gestures.
    def print_gestures(self):

        print "Gestures from " + self.gesture_file + ":"
        if not self.get_learned_gestures():
            print "None! (Teach a gesture.)"
        else:
            print "Name".ljust(25) + "Action"
            print ''.ljust(31, '=') + "\n"
            for g in self.get_learned_gestures():
                action_str = ' '.join(g.get_action())
                print (g.get_name() + ":").ljust(25) + action_str


# This class defines a simple writer-reader for saving BlueMote statistics.
class StatWR:

    def __init__(self, stat_file):
        self.stat_file = stat_file
        if not os.path.isfile(self.stat_file):
            f = open(self.stat_file, 'w')
            f.close()
            self.reset_stats()

    def get_stats(self):
        f = open(self.stat_file, 'r')
        success_tup = literal_eval(f.readline())
        f.close()
        return success_tup

    def update_stats(self, attempts, successes):
        f = open(self.stat_file, 'w')
        str_success_tup = str((attempts, successes))
        f.seek(0)
        f.truncate()
        f.write(str_success_tup)
        f.close()

    def get_attempts(self):
        return self.get_stats()[0]

    def get_successes(self):
        return self.get_stats()[1]

    # Resets the statistics for BlueMote to default.
    def reset_stats(self):
        self.update_stats(0,0)