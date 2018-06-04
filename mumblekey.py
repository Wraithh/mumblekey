#!/usr/bin/env python3

from libevdev import *
import sys
import os


# Configure hotkeys here
hotkey = EV_KEY.KEY_KPENTER
hotkey_toggle = EV_KEY.KEY_KPMINUS
ptt_key = EV_KEY.KEY_KPENTER

#hotkey = EV_KEY.KEY_A
#hotkey_toggle = EV_KEY.KEY_T
#ptt_key = EV_KEY.KEY_Q

# Keyboard grab prevents any key events from getting to the OS
grab_keyboard = True


if len(sys.argv) > 1:
    ev_in = sys.argv[1]
else:
    # Default input device
    ev_in = '/dev/input/by-id/usb-13ba_0001-event-kbd'
    #ev_in = '/dev/input/input0'

if not os.path.exists(ev_in):
    print("Usage: %s [<input_device>]" % sys.argv[0])
    print("eg. /dev/input/input0 or /dev/input/by-id/usb-13ba_0001-event-kbd")
    sys.exit(1)

try:
    fd = open(ev_in, 'rb', 0)
    d = Device(fd)
except:
    print("Couldn't open input device", ev_in)
    sys.exit(1)

if d.has(EV_KEY.BTN_LEFT):
    print(ev_id, 'does not look like a keyboard device')
    sys.exit(1)

d.enable(ptt_key)


try:
    d_out = d.create_uinput_device()
    #print(d_out.devnode)
except Exception as e:
    print("Could not create output device:", e)
    print("Probably you'll need to run this as root")
    sys.exit(1)

togglestate = False

syn = InputEvent(EV_SYN.SYN_REPORT, 0)
num_on  = [InputEvent(EV_LED.LED_NUML, 1)]
num_off = [InputEvent(EV_LED.LED_NUML, 0)]

event_PTT_ON  = [InputEvent(ptt_key, 1), syn]
event_PTT_OFF = [InputEvent(ptt_key, 0), syn]

print("PTT_KEY", ptt_key)
print("User hotkey", hotkey)
print("User toggle key", hotkey_toggle)

if grab_keyboard:
    d.grab()
    print("Successfully grabbed keyboard", ev_in)

while True:
    for e in d.events():
        if not e.matches(EV_KEY):
            continue
        if e.matches(hotkey):
            if e.matches(hotkey, 1):
                print('hotkey pressed down')
                d_out.send_events(event_PTT_ON)
            elif e.matches(hotkey, 0):
                print('hotkey released')
                togglestate = False
                d_out.send_events(event_PTT_OFF)
            continue

        if e.matches(hotkey_toggle, 1):
            if togglestate == False:
                togglestate = True
                d_out.send_events(num_on)
                d_out.send_events(event_PTT_ON)
                print('toggle key pressed, holding PTT')
            else:
                togglestate = False
                d_out.send_events(event_PTT_OFF)
                d_out.send_events(num_off)
                print('toggle key pressed, released PTT')


