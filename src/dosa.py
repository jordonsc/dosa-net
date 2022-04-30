#!/usr/bin/env python3

import argparse
import sys

import dosa

DEVICE_NAME = b"DOSA Network Tools"


def cli():
    parser = argparse.ArgumentParser(description='DOSA Network Tools')

    # Run a play
    parser.add_argument('-p', '--play', dest='play', action='store',
                        help='run a play (requires a SecBot on the network)')

    # Fire trigger
    parser.add_argument('-t', '--trigger', dest='trigger', default=False, nargs='?', action='store',
                        help='fire a trigger signal; target optional')

    # Request OTA update
    parser.add_argument('-o', '--ota', dest='ota', default=False, nargs='?', action='store',
                        help='send an OTA update request; target optional')

    # Send flush command
    parser.add_argument('-f', '--flush', dest='flush', default=False, nargs='?', action='store',
                        help='send a network flush command; target optional')

    # Network monitor
    parser.add_argument('-m', '--monitor', dest='monitor', action='store_const', const=True, default=False,
                        help='run a network monitor')

    # Legacy config tool
    parser.add_argument('-c', '--config', dest='config', action='store_const', const=True, default=False,
                        help='legacy configuration tool')

    args = parser.parse_args()

    # Main app
    comms = dosa.Comms(DEVICE_NAME)

    try:
        if args.play:
            play = dosa.Play(comms=comms)
            play.run(args.play)

        elif args.trigger is not False:
            trigger = dosa.Trigger(comms=comms)
            if args.trigger:
                trigger.fire(target=(args.trigger, 6901))
            else:
                trigger.fire()

        elif args.ota is not False:
            ota = dosa.Ota(comms=comms)
            if args.ota:
                ota.dispatch(target=(args.ota, 6901))
            else:
                ota.dispatch()

        elif args.flush is not False:
            flush = dosa.Flush(comms=comms)
            if args.flush:
                flush.dispatch(target=(args.flush, 6901))
            else:
                flush.dispatch()

        elif args.monitor is not False:
            monitor = dosa.Monitor(comms=comms)
            monitor.run()

        elif args.config is not False:
            cfg = dosa.Config(comms=comms)
            cfg.run()

        else:
            # New configuration tool
            pass

    except KeyboardInterrupt:
        print("")
        sys.exit(0)


if __name__ == "__main__":
    cli()
