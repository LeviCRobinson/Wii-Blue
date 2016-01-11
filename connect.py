#!/usr/bin/python

import wiiuse
import sys
import time
import os
from PerformedGesture import PerformedGesture
from WriterReader import GestureWriterReader
from ButtonHandler import ButtonHandler
from GestureMatcher import GestureMatcher
from GestureCreator import GestureCreator
from GeStat import GeStat

test_gesture = PerformedGesture(
    [(1, 1, 1, 1, 1), (2, 2, 2, 2, 2), (3, 3, 3, 3, 3), (4, 4, 4, 4, 4), (6, 5, 5, 5, 5)])  # Performed test gesture.
testing = False
num_motes = 1  # Number of wiimotes
FRAME_FREQ = 1  # The rate for capturing frames of information. Larger number = less frames captured
# i.e., every nth frame is captured and stored.
REPETITION_LIMIT = 5
STANDARD_SLEEP_TIME = 0.1

gestures_file = 'gestures.txt'
stats_file = 'gesture_stats.txt'
if len(sys.argv) > 2:
    if sys.argv[1] == 't':
        testing = True
    else:
        gestures_file = str(sys.argv[1])
        stats_file = str(sys.argv[2])

full_gestures_file = 'full_' + gestures_file

writer_reader = GestureWriterReader(
    gestures_file)  # Initializes the writer-reader to the either general use or testing.
stat = GeStat(stats_file, gestures_file)
full_writer_reader = GestureWriterReader(full_gestures_file)  # writer-reader for full gestures.
wiimotes = wiiuse.init(num_motes)
first_wm = wiimotes[0]
# Handles button press events of the wiimote.
button_handler = ButtonHandler(wiimotes, first_wm, num_motes)
# Object to perform gesture comparison.
gesture_matcher = GestureMatcher(writer_reader)
# Object that creates gesture objects.
gesture_creator = GestureCreator(gestures_file, wiimotes, first_wm, num_motes, FRAME_FREQ)


# The main prompt of the program
def main_prompt():
    print "\n\n**********************"
    print "\nHold B: perform a gesture \n2: Teach a gesture \nA: list all gestures.\nDown: Show gesture statistics \nTo quit, press the + button."
    print "To erase all gestures, press the - button."
    print "**********************\n\n"


def test(gesture):
    print gesture_matcher.evaluation_function(gesture)


# Pretty star wave to stdout.
def star_wave(repetitions=1):
    """

    :rtype: Nothing. Prints only.
    """
    star_array = ["    *    ", "   * *   ", "  *   *  ", " *     * ", "*       *"]
    star_array += reversed(star_array)

    for i in range(0, 30 * repetitions):
        print star_array[i % len(star_array)]
        time.sleep(STANDARD_SLEEP_TIME / 5)


def intro_prompt():
    if os.name != 'nt':
        print "\n\n*************************************"
        time.sleep(STANDARD_SLEEP_TIME)
        print "*************************************"
        time.sleep(STANDARD_SLEEP_TIME)
        print "*************************************\n"
        time.sleep(STANDARD_SLEEP_TIME)
        print "Press 1 & 2 to connect"

        found_motes = wiiuse.find(wiimotes, num_motes, 1)  # Find one remote, and wait up to 1 second to find it.

        # If no remotes are found...
        if not found_motes:
            print "No remotes found!  Exiting."
            sys.exit(1)
        else:
            print "... Found remote."

        connected = wiiuse.connect(wiimotes, num_motes)

        if connected:
            print 'Connected to %i wiimotes!' % connected
        else:
            print "Failed to connect.  Exiting."
            sys.exit(1)

        wiiuse.set_leds(first_wm, wiiuse.LED[0])

        print "Enabling motion sense..."
        time.sleep(STANDARD_SLEEP_TIME)
        wiiuse.motion_sensing(first_wm, 1)  # Enable motion sensing.
        time.sleep(STANDARD_SLEEP_TIME)

        print "Enabling IR...\n"
        time.sleep(STANDARD_SLEEP_TIME)
        wiiuse.set_ir(first_wm, 1)  # Enable IR (No sensor bar yet.)
        time.sleep(STANDARD_SLEEP_TIME)

        print "*************************************"
        time.sleep(STANDARD_SLEEP_TIME)
        print "*************************************"
        time.sleep(STANDARD_SLEEP_TIME)
        print "*************************************\n"

        time.sleep(STANDARD_SLEEP_TIME)
        star_wave()
        print "\nLet's begin!\n"
        star_wave()


# Recommends that the user re-teach a gesture for clarity.
def recommend_relearn(gesture):
    confirm = raw_input(gesture.get_name() + " has a low success rate.  Relearn? (y/n): ")

    if confirm.lower() == 'y':
        writer_reader.delete_gesture(gesture.get_name())
        gesture_creator.learn_gesture(REPETITION_LIMIT)
        gesture_matcher.update_known_gestures()
        gesture_creator.update_gestures()
    else:
        return


################################################################
#
# Begin BlueMote!
#
################################################################

done = False
i = 0

intro_prompt()
main_prompt()

# Main usage loop
while not done:
    # Poll the wiimotes for button/motion events
    r = wiiuse.poll(wiimotes, num_motes)

    if r != 0:
        # If there are any events, check for a pressed button
        button_pressed = button_handler.press_event()

        if button_pressed == wiiuse.button['B']:
            os.system('clear')
            print "\nRecognizing gesture...\n"

            # Collect data from the user's performed gesture.
            performed_gesture = gesture_creator.perform_gesture()

            if performed_gesture is None:
                # If the gesture has no length, prompt the user to try again
                time.sleep(STANDARD_SLEEP_TIME * 5)
                print "..."
                time.sleep(STANDARD_SLEEP_TIME * 5)
                print "Uh-oh!  That gesture had no length.  Try again."
                time.sleep(STANDARD_SLEEP_TIME * 5)
                main_prompt()
                continue

            # if testing:
            #     performed_gesture = test_gesture
            #     test(performed_gesture)

            # Weight the sensor readings based on how important they are to the gesture.
            gesture_matcher.evaluation_function(performed_gesture)
            # Otherwise, match the performed gesture to the closest learned gesture.
            matched_gesture = gesture_matcher.greatest_closest_recognition(performed_gesture)
            if matched_gesture is None:
                # If there is no matched gesture, then none are known.  Prompt the user to teach a gesture.
                print "\nNo known gestures!  Teach a gesture to use gesture recognition.\n"
                continue

            print "Did you mean to perform", matched_gesture.get_name() + "?"
            print "Press A to confirm, B if you meant something else, or + to cancel."
            confirmed = False

            while not confirmed:
                r = wiiuse.poll(wiimotes, num_motes)
                confirm_button = button_handler.press_event()
                if confirm_button == wiiuse.button['+']:
                    confirmed = True
                    continue
                elif confirm_button == wiiuse.button['A']:
                    # If the user performed the correct action
                    print "\nSuccess! Performing action...\n"
                    matched_gesture.call_action()

                    stat.confirm(matched_gesture, True)  # Update gesture statistics with a success.
                    # Factor the successful gesture into the gesture's average
                    matched_gesture.update_and_average(performed_gesture.get_frames())
                    # Update the matched gesture on disk
                    writer_reader.update_gesture(matched_gesture)
                    confirmed = True
                elif confirm_button == wiiuse.button['B']:
                    while not confirmed:
                        intended_gesture_name = raw_input("Whoops!  What was your intended gesture?:")
                        intended_gesture = writer_reader.get_gesture_from_name(intended_gesture_name)
                        if intended_gesture is not None:
                            confirmed = True
                            stat.confirm(intended_gesture, False)

                            # If failed gesture, instead update the INTENDED
                            # gesture with the performed gesture iteration
                            intended_gesture.update_and_average(performed_gesture.get_frames())

                            # Suggest that the user re-teach a gesture that is inconsistently successful.
                            if (stat.get_gesture_success_rate(intended_gesture) < 0.6 and
                                    intended_gesture.get_attempts() > 5):
                                recommend_relearn(intended_gesture)

                            # Print statistics regarding the intended gesture
                            print "\n" + (intended_gesture.get_name() + " success rate:").ljust(30) + str(
                                stat.get_gesture_success_rate(intended_gesture))
                            # Update the intended gesture on disk.
                            writer_reader.update_gesture(intended_gesture)

            # Update gestures in memory as necessary.
            gesture_creator.update_gestures()
            gesture_matcher.update_known_gestures()

            # Print statistics regarding the matched gesture and total statistics.
            print "\n" + (matched_gesture.get_name() + " success rate:").ljust(30) + str(
                stat.get_gesture_success_rate(matched_gesture))
            print "Total success rate:".ljust(30) + str(stat.get_total_success_rate())
            main_prompt()

        elif button_pressed == wiiuse.button['2']:
            os.system('clear')
            print "\nLearning gesture.\n"
            # Learn the gesture.
            gesture_creator.learn_gesture(REPETITION_LIMIT)
            # Update gestures in memory as necessary.
            gesture_matcher.update_known_gestures()
            gesture_creator.update_gestures()
            main_prompt()

        elif button_pressed == wiiuse.button['-']:
            os.system('clear')
            print "Are you sure you want to delete all your gestures?  Press A to confirm, or B to cancel."
            confirmed = False
            while not confirmed:
                r = wiiuse.poll(wiimotes, num_motes)
                confirm_button = button_handler.press_event()
                if confirm_button == wiiuse.button['A']:
                    print "Okay! Deleting gestures!"
                    time.sleep(0.5)
                    confirmed = True
                    writer_reader.delete_gestures()  # Delete gestures from the gesture file.
                    full_writer_reader.delete_gestures()  # Delete full gestures from its file
                    gesture_matcher.update_known_gestures()  # Update the currently known gestures in gesture matcher
                    gesture_creator.update_gestures()  # Update the currently known gestures in gesture creator.
                    stat.reset_all_stats()  # Reset statistics to no attempts, and no successes.
                elif confirm_button == wiiuse.button['B']:
                    print "Canceled! (Phew)"
                    confirmed = True

            main_prompt()

        elif button_pressed == wiiuse.button['A']:
            os.system('clear')
            writer_reader.print_gestures()
            main_prompt()

        elif button_pressed == wiiuse.button['+']:
            os.system('clear')
            print "Exiting!"
            time.sleep(2 * STANDARD_SLEEP_TIME)
            done = True

        elif button_pressed == wiiuse.button['Up']:
            os.system('clear')
            stat.reset_all_stats()
            stat.print_stats()
            gesture_creator.update_gestures()  # Update the gestures in memory
            gesture_matcher.update_known_gestures()  # Update the gestures in memory
            main_prompt()
        elif button_pressed == wiiuse.button['Down']:
            os.system('clear')
            stat.print_stats()
            main_prompt()

# Disconnect the wiimote and exit.
gesture_creator.update_gestures()
gesture_matcher.update_known_gestures()
stat.print_stats()
wiiuse.disconnect(first_wm)
sys.exit(1)
