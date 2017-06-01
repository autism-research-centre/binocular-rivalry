from psychopy import core, visual, event, monitors, gui, data
from datetime import datetime
import random  # random for randomisation
import numpy as np  # for array handling
import os
import os.path

# Stimulus Parameters
trialdur = 8.0  # trial duration in seconds
breakdur = 4.0  # minimum duration of a break in seconds

totaltrials = 4

stimsize = 8  # size of stimuli in deg of visual angle
repetitions = 1  # how many trials per condition

screenrefresh = 60.0  # refresh rate of screen

simulationpercepts = [1.5, 3.5]  # interval for simulated percept length
# durations will be sampled evenly from this interval

wedges = [8, 16]  # how many "pie" slices in stimulus
concentrics = [6, 3]  # how many "rings" in stimulus

colors = [1, 0, 0.9]  # the rgb layers of your stimulus
# the 0.8 is due to the anaglyph blue being brighter than red

# What buttons you want to use, and what image they correspond to:
responses = {'right': 'red', 'up': 'mixture', 'left': 'blue'}

# Get participant information:
sessionInfo = {'subject': 'test',
               'time': datetime.now().strftime('%Y-%m-%d %H-%M')}
assert gui.DlgFromDict(dictionary=sessionInfo, title='Pupil Dilation').OK

# Set the screen parameters: (This is important!)
screen = monitors.Monitor("testMonitor")
screen.setSizePix([1680, 1050])
screen.setWidth(47.475)
screen.setDistance(57)
# Open the display window:
win = visual.Window([500, 500], allowGUI=True, monitor=screen,
                    units='deg', fullscr=True)


# Make the vergence cues (using list comprehension)
square = visual.Circle(win, radius=np.sqrt(2) * stimsize / 2,
                       fillColor=None, autoDraw=True, edges=128,
                       lineWidth=2, pos=[0, 0], lineColor=-1)
# Make fixation cross (using list comprehension)
fixation = visual.GratingStim(win, tex="sqr", mask="cross", sf=0, size=0.5,
                              pos=[0, 0], color=-1,
                              autoDraw=True)
# Make a dummy message
message = visual.TextStim(win, units='norm', pos=[0, 0.75], height=0.06,
                          alignVert='center', alignHoriz='center',
                          text='')
backreport = visual.TextStim(win, units='norm', pos=[0.9, -0.9], height=0.03,
                             alignVert='center', alignHoriz='center',
                             text='')


# The arrays needed to construct the stimuli:
# Mask
mask = np.concatenate([np.array([-1]), np.ones(min(concentrics))])
# Checkerboards
texlayer = [np.repeat(
    np.repeat(
            np.tile(np.array([[1, 0], [0, 1]]), (concentrics[stim] +
                                                 concentrics[stim] /
                                                 min(concentrics),
                                                 wedges[stim] / 2)),
            concentrics[stim - 1] + concentrics[stim - 1] /
            min(concentrics), axis=0
            ),
    6 * wedges[stim - 1], axis=1
) * color * 2 - 1
    for stim, color in enumerate([colors[0], colors[2]])]
# Blank (all black)
blanklayer = np.zeros(texlayer[0].shape) - 1

# Make stimuli. This will be remade during each trial anyways tho
stimuli = visual.RadialStim(win, size=stimsize, pos=fixation.pos,
                            mask=mask, colorSpace='rgb', angularRes=600,
                            # Radial and Angular Frequencies:
                            radialCycles=0.5,
                            angularCycles=1,
                            # Baseline Texture:
                            tex=np.dstack((texlayer[0],
                                           blanklayer,
                                           texlayer[1]))
                            )


# Define an instruction function
def instruct(displaystring):
    message.text = displaystring + "\nPress [space] to continue."
    message.draw()
    win.flip()
    if 'escape' in event.waitKeys(keyList=['space', 'escape']):
        raise KeyboardInterrupt


def trigger(value):
    print(value)


# function for demonstration
def demonstrate():

    core.wait(0.5)
    # Draw Red:
    message.text = ("This is what a red stimulus will look like. In "
                    "the experiment, you would report seeing this by pressing "
                    "right.\nPress [space] to continue.")
    frame = 0
    while 'space' not in event.getKeys(keyList=['space']):
        stimuli.tex = np.dstack((texlayer[0],
                                 blanklayer,
                                 blanklayer))
        message.draw()
        stimuli.draw()
        win.flip()
    # Clear & Flush
    win.flip()
    event.getKeys()
    core.wait(1)

    # Draw Blue:
    message.text = ("And this is what a blue stimulus will look like. "
                    "In the experiment, you would report seeing this by "
                    "pressing left.\nPress [space] to continue.")
    frame = 0
    while 'space' not in event.getKeys(keyList=['space']):
        stimuli.tex = np.dstack((blanklayer,
                                 blanklayer,
                                 texlayer[1]))
        message.draw()
        stimuli.draw()
        win.flip()
    # Clear & Flush
    win.flip()
    event.getKeys()
    core.wait(1)

    # Draw both rotating:
    message.text = ("And this is what the two will look like together. "
                    "In the experiment, you will have to report what "
                    "you are seeing at any given point by pressing "
                    "either [left], [right], or [up]."
                    "\nPress [space] to continue.")
    frame = 0
    while not event.getKeys(keyList=['space']):
        stimuli.tex = np.dstack((texlayer[0],
                                 blanklayer,
                                 texlayer[1]))
        message.draw()
        stimuli.draw()
        win.flip()
    # Clear & Flush
    win.flip()
    core.wait(1)


# Define a trial function:
def rivaltrial(info):

    # Arrays to keep track of responses:
    keyArray = np.zeros((int(trialdur * screenrefresh), 3),
                        dtype=int)  # start with up pressed
    timeArray = np.zeros((int(trialdur * screenrefresh), 1),
                         dtype=float)  # start at time 0

    # Wait for participant to start:
    message.text = ("Trial number " + str(1 + trials.thisN) + " of " +
                    str(trials.nTotal) +
                    ". Remember: UP is for mixture, LEFT is for "
                    "blue, and RIGHT is for red.\nPress and hold [up] "
                    "to begin the trial.")
    message.draw()
    win.flip()
    if "escape" in event.waitKeys(keyList=['up', 'escape']):
        raise KeyboardInterrupt("You interrupted the script manually.")

    # This will keep track of response time:
    trialClock = core.Clock()
    win.callOnFlip(trialClock.reset)

    for frame in range(int(trialdur * screenrefresh)):

        # Update the stimulus texture
        stimuli.tex = np.dstack((texlayer[0],
                                 blanklayer,
                                 texlayer[1]))
        stimuli.draw()
        # Flip
        win.flip()

        # Check response & save to array
        currKeys = event.getKeys()
        keyArray[frame, :] = [response in currKeys
                              for response in responses.keys()]
        timeArray[frame] = trialClock.getTime()
        if keyArray[frame, 1]:
            backreport.text = 'mixture'
        elif keyArray[frame, 0]:
            backreport.text = 'red'
        elif keyArray[frame, 2]:
            backreport.text = 'blue'
        backreport.draw()

    # After trial is over, clear the screen
    backreport.text = ''
    win.flip()

    # force first key to be mix
    keyArray[0, :] = np.array([0, 1, 0])
    # find all rows that are zero
    notblanks = np.any(keyArray, axis=1)
    # remove them
    keyArray = keyArray[notblanks, :]
    timeArray = timeArray[notblanks, :]

    # return the two arrays
    return keyArray, timeArray


# Define a break function:
def rivalbreak():
    fixation.autoDraw = False  # disable fixation
    # Display message
    for sec in range(int(breakdur)):
        message.text = "Break for %d seconds." % (breakdur - sec)
        message.draw()
        win.flip()
        # Pause for a second (interrupt if key pressed)
        if event.waitKeys(maxWait=1, keyList=['escape']):
            # Escape stops script:
            raise KeyboardInterrupt("You interrupted the script manually.")
    fixation.autoDraw = True  # enable fixation
    win.flip()


# Explain the experiment
instruct("This experiment is called binocular rivalry, and you will need the "
         "red and blue glasses to do so. Your right eye should be viewing "
         "through a red lense, and your left eye should be viewing through "
         "a blue lens.")
instruct("In this experiment, we will be showing a different pattern "
         "to each of your eyes. This will mean that for a while, you will "
         "be seeing one image, and then it will suddenly switch.")
instruct("All you need to do during each trial of this experiment is "
         "report what you are seeing continuously. To do so, you have "
         "to hold down either the UP arrow, the LEFT arrow, or the RIGHT "
         "arrow.")
instruct("These buttons stand for different images:\nThe RIGHT arrow stands "
         "for the RED image.\nThe LEFT arrow stands for the blue image.\n"
         "And the UP arrow stands for a mixture, so for example, when about "
         "50% is red and 50% is blue.")
instruct("It's rare for an image to be 100% blue or red, but you should "
         "still only press the UP arrow when you can't decide which color "
         "is dominant.")
instruct("Please report what you are seeing continuously. So, during one trial,"
         " you should be pressing one button at any one time. Next, we will "
         "demonstrate what the images are like.")

# demonstrate the stimuli:
demonstrate()

# check before starting:
instruct("If you have any other questions, please ask the experimenter now. "
         "Otherwise, go ahead to start the experiment.")

# randomise trial sequence:
trials = data.TrialHandler(
    [{'pattern': [0, 1] if pattern else [1, 0],
      'flickering': False,
      'simulation': True if trialtype == 2 else False}
     for pattern in range(2)
     for trialtype in range(2)],
    repetitions)

# make a directory for data storage
# datadir = os.path.join(os.getcwd(), 'data',  sessionInfo[
#                        'time'] + sessionInfo['subject'], '')
# os.makedirs(datadir)

# Loop through trials:
keylists = []
timelists = []

for trial in trials:
    keys, times = rivaltrial(trial)
    keylists.append(keys)
    timelists.append(times)
    print(keys)
    # Take a break (not on last)
    if trials.thisN < totaltrials - 1:
        rivalbreak()
    else:
        break

# work out the average mix percept
mixpercepts = []
for times, keys in zip(timelists, keylists):
    durations = np.diff(np.concatenate(
        (times.flatten(), np.zeros(1) + trialdur)
    ))
    durations = durations[keys[:, 1] == 1]
    for dur in durations:
        mixpercepts.append(dur)

print(keylists)
print(timelists)
print(mixpercepts)
avmix = np.mean(mixpercepts)

message.text = ("Nice work, thanks for taking part!\n\n"
                "The average time you saw the mixed percept for was \n" +
                str(round(avmix, 1)) + " seconds. Let the experimenters know!"
                "\n\nPress any key to finish.")
message.draw()
win.flip()
core.wait(2)
event.waitKeys()

# Close everything neatly
win.close()
core.quit()
