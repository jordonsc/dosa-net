#!/usr/bin/env python3

import argparse
import sys
import time
import daemon.pidfile

import dosa
from dosa.secbot import SecBot

DEVICE_NAME = b"DOSA Security Bot"


def run_app(voice, engine):
    first_run = True
    while True:
        try:
            comms = dosa.Comms(DEVICE_NAME)
            secbot = SecBot(comms, voice=voice, engine=engine)
            secbot.run(announce=first_run)
        except Exception as e:
            # Most commonly this will be a network error (OSError or boto error)
            print("Fault: " + str(e))
            first_run = False
            time.sleep(1)


if __name__ == "__main__":
    # Arg parser
    parser = argparse.ArgumentParser(description='DOSA Security Bot')

    parser.add_argument('-d', '--daemon', dest='daemon', action='store_const', const=True, default=False,
                        help='run in background')
    parser.add_argument('-p', '--pid-file', dest='pid', action='store', help='daemon PID file')
    parser.add_argument('-v', '--voice', dest='voice', action='store', default="Emma",
                        help='bot voice (Emma, Amy, Brian)')
    parser.add_argument('-e', '--engine', dest='engine', action='store', default="neural",
                        help='TTS engine (neural, standard)')

    args = parser.parse_args()

    if args.daemon:
        with daemon.DaemonContext(pidfile=daemon.pidfile.TimeoutPIDLockFile(args.pid) if args.pid else None):
            run_app(args.voice, args.engine)
    else:
        try:
            run_app(args.voice, args.engine)
        except KeyboardInterrupt:
            print("")
            sys.exit(0)
