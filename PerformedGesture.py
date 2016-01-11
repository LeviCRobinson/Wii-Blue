# A class defining a performed gesture for BlueMote
# Differs from a LearnedGesture in that it has no name or action --
# just movement data.


class PerformedGesture:
    def __init__(self, frames):
        self.frames = frames  # Readings defining the gesture
        self.gesture = self.frames

    # Returns the roll at the given frame index.
    def get_roll(self, index):
        if index >= len(self.frames):
            print "PerformedGesture.get_roll: Error.  Index out of bounds."
            return
        return self.frames[index][0]

    # Returns the pitch at the given frame index.
    def get_pitch(self, index):
        if index >= len(self.frames):
            print "PerformedGesture.get_pitch: Error.  Index out of bounds."
            return
        return self.frames[index][1]

    # Returns the x coordinate at the given frame index.
    def get_X(self, index):
        if index >= len(self.frames):
            print "PerformedGesture.get_x: Error.  Index out of bounds."
            return
        return self.frames[index][2]

    # Returns the y coordinate at the given frame index.
    def get_Y(self, index):
        if index >= len(self.frames):
            print "PerformedGesture.get_y: Error.  Index out of bounds."
            return
        return self.frames[index][3]

    # Returns the z coordinate at the given frame index.
    def get_Z(self, index):
        if index >= len(self.frames):
            print "PerformedGesture.get_z: Error.  Index out of bounds."
            return
        return self.frames[index][4]

    # Returns a full frame
    def get_frame(self, index):
        if index >= len(self.frames):
            print "PerformedGesture.get_frame: Error.  Index out of bounds."
            return
        return self.frames[index]

    # Returns the entire list of frames representing the iteration of the Gesture.
    def get_frames(self):
        return self.frames

    # Returns the length of the gesture, in frames.
    def get_length(self):
        return len(self.frames)

    # Returns the tuple that contains the gesture name and frames.
    def get_gesture(self):
        return self.gesture
