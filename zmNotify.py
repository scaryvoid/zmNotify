#!/usr/bin/env python

# Desktop notifications of zm alarms using pyzm

import pyzm, getpass, traceback, gi, time, playsound, argparse, os, datetime
import pyzm.api as zmapi
import pyzm.ZMMemory as zmmemory
import pyzm.helpers.utils as utils
from pyzm.helpers.Base import ConsoleLog
from gi.repository import Notify


zmPath = os.path.realpath(__file__).replace('/zmNotify.py', '')
logFile = os.path.join(zmPath, "zmNotify.log")
alertSoundFile = os.path.join(zmPath, 'alert.ogg')
lastidFile = os.path.join(zmPath, 'lastid')
logger = ConsoleLog()
logger.set_level(1) # 2 will display each poll
conf = utils.read_config(os.path.join(zmPath, 'secrets.ini'))
Notify.init("zmNotifyMessage")

api_options  = {
    'apiurl': utils.get(key='ZM_API_PORTAL', section='secrets', conf=conf),
    'portalurl':utils.get(key='ZM_PORTAL', section='secrets', conf=conf),
    'user': utils.get(key='ZM_USER', section='secrets', conf=conf),
    'password': utils.get(key='ZM_PASSWORD', section='secrets', conf=conf),
    'logger': logger
}

zmapi = zmapi.ZMApi(options=api_options)

event_filter = {
    'object_only':True,
    'min_alarmed_frames': 2,
    'max_events':1,
}


def writelog(string):
    with open(logFile, 'a') as f:
        f.write("{0} {1}\n".format(datetime.datetime.now(), string))


def notify(string, seconds):
    writelog("Alert!")
    playsound.playsound(alertSoundFile)    
    n = Notify.Notification.new(string)
    n.set_timeout(seconds * 1000)
    n.show()


def main():
    parser = argparse.ArgumentParser(description='Send zoneminder alarm notifications to the desktop.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', metavar='<seconds>', nargs=1, default=[10], type=int, help='Delay time between polling event server.')
    parser.add_argument('-t', metavar='<seconds>', nargs=1, default=[10], type=int, help='How long to display notification.')
    args = parser.parse_args()

    # get lastid from file
    if not os.path.exists(lastidFile):
        with open(lastidFile, 'w') as f:
            f.write("0")

    with open(lastidFile, 'r') as f:
        lastid = f.read()

    writelog("Starting lastid: {0}".format(lastid))

    while 1:
        # get events list
        cam_events = zmapi.events(event_filter)
        for e in cam_events.list():
            eid = e.id()
            cause = e.cause()
            notes = e.notes()
            
            if eid > int(lastid):
                writelog("New Event Found: {0} lastid: {1}".format(eid, lastid))
                lastid = eid
                with open(lastidFile, 'w') as f:
                    f.write("{0}".format(eid))
                notify("Event:{0} Cause:{1} Notes:{2}".format(eid, cause, notes), args.t[0])
                #cam_events.list()[0].download_image()
        
        time.sleep(args.d[0])


if __name__ == "__main__":
    main()
