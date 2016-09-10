#!/usr/bin/python
import cwiid
import sys
import time

import pypm

from txosc import osc as OSC
from txosc import sync as SYNC

btn_A     = 0x0008
btn_one   = 0x0002
btn_two   = 0x0001
btn_left  = 0x0100
btn_right = 0x0200
btn_up    = 0x0800
btn_down  = 0x0400
btn_minus = 0x0010
btn_plus  = 0x1000
btn_home  = 0x0080
btn_shoot = 0x0004

class MIDISender:
    def __init__(self,device):
        self.midi_out = None
        for id in range(pypm.CountDevices()):
            interf,name,inp,outp,opened = pypm.GetDeviceInfo(id)
            if (outp == 1 and name == device):
                self.midi_out = pypm.Output(id,0)
                break
        if self.midi_out == None:
            raise Exception("No output device "+device+" found ...")

    def mute(self,channel):
        print "muting", channel
        for v in range(100,0,-2):
            self.midi_out.Write([[[0xb0,channel,v],pypm.Time()]])
            time.sleep(0.001)

    def unmute(self,channel):
        print "unmuting", channel
        for v in range(0,100,2):
            self.midi_out.Write([[[0xb0,channel,v],pypm.Time()]])
            time.sleep(0.001)

    def play_jingle(self, n):
        print "playing jingle", n
        self.midi_out.Write([[[0x90,n,127],pypm.Time()]])
        time.sleep(0.1)
        self.midi_out.Write([[[0x80,n,0],pypm.Time()]])

    def stop_jingles(self):
        print "stopping jingles"
        self.midi_out.Write([[[0xb0,126,127],pypm.Time()]])
        time.sleep(0.1)
        self.midi_out.Write([[[0xb0,126,0],pypm.Time()]])

#        self.midi_out.Write([[[0xb0,channel,0],pypm.Time()]])

class OSCSender:

    def __init__(self,host="localhost",port=3819):
        self.sender = SYNC.UdpSender(host,port)

    def _simple_msg(self,msg):
        self.sender.send(OSC.Message(msg))

    def add_marker(self):
        self._simple_msg("/add_marker")

    def rec_prepare(self):
        self.sender.send(OSC.Message("/access_action", "Editor/script-action-2"))

    def play(self):
        self._simple_msg("/transport_play")

    def stop(self):
        self._simple_msg("/transport_stop")

midi_sender = MIDISender("Midi Through Port-0")
osc_sender = OSCSender()

class WiiButtonState(object):
    def __init__(self):
        self.button_state = {
            btn_A:     False,
            btn_one:   False,
            btn_two:   False,
            btn_left:  False,
            btn_right: False,
            btn_up:    False,
            btn_down:  False,
            btn_minus: False,
            btn_plus:  False,
            btn_home:  False,
            btn_shoot: False
        }

        self.button_funcs = {}

    def callback(self,messages,time):
        for msgType, msgContent in messages:
            if msgType != cwiid.MESG_BTN:
                continue
            self.buttonEvent(msgContent)

    def buttonEvent(self,state):
        for btn,old_state in self.button_state.items():
            new_state = state & btn
            if new_state != old_state:
                self.button_state[btn] = new_state
                if btn in self.button_funcs:
                    press_func, rel_func = self.button_funcs[btn]
                    if new_state:
                        press_func()
                    else:
                        rel_func()


class MutingWii(WiiButtonState):
    def __init__(self,mutingChannel):
        super(MutingWii,self).__init__()
        self.mutingChannel = mutingChannel
        self.button_funcs[btn_shoot] = (self.mute,self.unmute)

    def mute(self):
        self.device.led = cwiid.LED1_ON
        midi_sender.mute(self.mutingChannel)

    def unmute(self):
        self.device.led = 0
        midi_sender.unmute(self.mutingChannel)


class MasterWii(MutingWii):
    def __init__(self,mutingChannel):
        super(MasterWii,self).__init__(mutingChannel)
        self.button_funcs[btn_one] = (self.jingle1_play,self.leds_off)
        self.button_funcs[btn_two] = (self.jingle2_play,self.leds_off)
        self.button_funcs[btn_home] = (self.rec_prepare,self.leds_off)
        self.button_funcs[btn_A] = (self.set_mark,self.leds_off)
        self.button_funcs[btn_up] = (self.play,self.leds_off)
        self.button_funcs[btn_down] = (self.stop,self.leds_off)

    def jingle1_play(self):
        print "Jingle1 play"
        self.device.led = cwiid.LED2_ON
        midi_sender.play_jingle(0)

    def jingle2_play(self):
        print "Jingle2 play"
        self.device.led = cwiid.LED2_ON
        midi_sender.play_jingle(1)

    def jingles_stop(self):
        midi_sender.stop_jingles()

    def rec_prepare(self):
        print "Recplay"
        self.device.led = cwiid.LED3_ON
        osc_sender.rec_prepare()

    def play(self):
        osc_sender.play()

    def stop(self):
        osc_sender.stop()

    def set_mark(self):
        print "Set mark"
        self.device.led = cwiid.LED4_ON
        osc_sender.add_marker()

    def leds_off(self):
        self.device.led = 0



def do_nothing():
    pass


execfile('device_config')

def make_connections(conns):
    for id,instance in devices.items():
        if id in conns:
            continue
        print "Connecting", id,
        try:
            wiimote = cwiid.Wiimote(id)
            print "success",
            wiimote.rpt_mode = cwiid.RPT_BTN
            print "report buttons",
            wiimote.mesg_callback = instance.callback
            instance.device = wiimote
            wiimote.enable(cwiid.FLAG_MESG_IFC)
            conns.append(id)
        except:
            print "failed"
    return conns


if __name__ == "__main__":
    conns = []
    while True:
        make_connections(conns)
        time.sleep(1)
