# wiimote recording control
Control your recordings by multiple wiimotes – one for each speaker

## Use your wiimotes to do the following things:

* Mute an individual speaker's track
  Whenever a speaker needs to cough, sip water, whatever during the recoding
  while others are speaking, you don't want the sound of the cough in your
  final podcast publication. Give every speaker a wiimote and tell them to
  press the button to mute themselves.

* Start and stop jingles
  You can declare one wiimote as the moderator's. The moderator's wiimote can
  by the B-button trigger the jingle.

* Set chapter marks (to be implemented)

* Start and stop the recording (to be implemented)

* other ideas


## How it works

It's a python program that connects to all the wiimotes you configure. On a
button press event it sends MIDI signals that you can connect to your jack
clients like Ardour or some audio player like idjc.


## What you need

The following ubuntu packages or equivalents

* python-cwiid
* python-pypm


## How to use it

By now it's a hack.

Copy sample_device_config to device_config and edit the MAC-Adresses to the
MAC-Adresses of your wiimotes.

	devices = {
		"0C:FC:83:A4:95:E9": MasterWii(100),
		"0C:FC:83:A4:1A:87": MutingWii(101),
		"00:17:AB:39:B2:EE": MutingWii(102),
		"00:17:AB:39:E7:CC": MutingWii(103),
	}

In this example the device `0C:FC:83:A4:95:E9` is the so called MasterWii. This
is meant to be the moderator's one that can not only mute the speaker's track
but also trigger jingles and other moderator's stuff.

The paramters given to MasterWii() or MutingWii() is the MIDI channel by which
the muting singnal will be sent, when the speaker presses the button.

Use Ardour's [MIDI-learn feature][1] to bind the Muting signals to a speakers
track. Setup your recording environment with all the speakers tracks.
Ctrl-Middle-click onto the fader of a speaker's track. Then press the A-button
of the speaker's wiimote. After this the fader should drop when the button is
pressed.

Note that for the moment you must manually set the fader automation mode to
"Write".

[1]: http://manual.ardour.org/using-control-surfaces/midi-learn/


## What is still to be done ...

... in the order of importance

* Support OSC to control the DAW.
* Button to set a chapter mark
* Button to start recording (that also makes sure that the fader automation
  modes are set)
* Documentation

* GUI-support? (I won't do it, I will accept it if you do.)
