# This class defines a GeStats object, which keeps track of statistics regarding BlueWand.
from WriterReader import StatWR
from WriterReader import GestureWriterReader


class GeStat:

    def __init__(self, stat_file, gesture_file):
        self.stat_wr = StatWR(stat_file)
        self.gesture_writer_reader = GestureWriterReader(gesture_file)
        self.total_attempts = self.stat_wr.get_attempts()
        self.total_successes = self.stat_wr.get_successes()

    # Updates a gesture's statistics according to whether or not
    # a gesture was performed successfully.
    def confirm(self, gesture, was_successful):

        # Increment the gesture attempts, and the total attempts
        gesture.incr_attempts()
        self.incr_total_attempts()

        # If the gesture was confirmed to be successful, increment the gesture successes
        # and the total successes.
        if was_successful:
            gesture.incr_successes()
            self.incr_total_successes()

        self.gesture_writer_reader.update_gesture(gesture)

    # Returns the success rate of a gesture.
    # If the gesture has never been recognized, returns a success rate of 0.
    @staticmethod
    def get_gesture_success_rate(gesture):

        if gesture.get_attempts() != 0:
            success_rate = float(gesture.get_successes())/float(gesture.get_attempts())
            return success_rate
        else:
            # Gesture has never been recognized.
            return 0

    # Convenience method. Returns failure rate of a Gesture.
    # i.e., the rate of times this gesture was mistakenly performed.
    def get_failure_rate(self, gesture):
        return 1-self.get_gesture_success_rate(gesture)

    # Returns the total success rate of BlueMote. (total successes over total attempts).
    def get_total_success_rate(self):
        if self.total_attempts != 0:
            return float(self.total_successes) / float(self.total_attempts)
        else:
            return 0

    # Increments successes, and updates the stats file.
    def incr_total_successes(self):
        self.total_successes += 1
        self.stat_wr.update_stats(self.total_attempts, self.total_successes)

    # Increments attempts. Also updates the stats file.
    def incr_total_attempts(self):
        self.total_attempts += 1
        self.stat_wr.update_stats(self.total_attempts, self.total_successes)

    # Sets total successes to the given number.  Updates stats file.
    def set_total_successes(self, num_successes):
        self.total_successes = num_successes
        self.stat_wr.update_stats(self.total_attempts, self.total_successes)

    # Sets total attempts to the given number.  Updates stats file.
    def set_total_attempts(self, num_attempts):
        self.total_attempts = num_attempts
        self.stat_wr.update_stats(self.total_attempts, self.total_successes)

    # Resets the total statistics to 0 attempts and 0 successes.
    def reset_total_stats(self):
        self.stat_wr.reset_stats()
        self.set_total_attempts(0)
        self.set_total_successes(0)

    # Resets all gesture statistics to 0 attempts and 0 successes
    def reset_gesture_stats(self):
        known_gestures = self.gesture_writer_reader.get_learned_gestures()
        for g in known_gestures:
            g.reset_stats()

        self.gesture_writer_reader.overwrite_gestures(known_gestures)

    # Resets all gesture statistics and the total statistics.
    def reset_all_stats(self):
        self.reset_total_stats()
        self.reset_gesture_stats()

    # Prints the statistics of each gesture and the total stats.
    def print_stats(self):
        known_gestures = self.gesture_writer_reader.get_learned_gestures()
        print "\n".ljust(15+18+12+12, '*')
        print "Statistics:"
        print "\n\n" + "Number of known gestures: " + str(len(known_gestures))
        print "\n\n   Name".ljust(15) + "Success rate".ljust(18) + "Successes".ljust(12) + "Attempts".ljust(12) \
              + "\n"
        for g in known_gestures:
            print "   " + g.get_name().ljust(15) + str(self.get_gesture_success_rate(g)).ljust(18) + \
            str(g.get_successes()).ljust(12) + str(g.get_attempts()).ljust(12)

        print "\n   Total Success Rate".ljust(25) + "Total Successes".ljust(20) + "Total Attempts".ljust(20)
        print "   " + str(self.get_total_success_rate()).ljust(25) + str(self.total_successes).ljust(20) \
        + str(self.total_attempts).ljust(20) + "\n\n"

