#!/usr/bin/env python3
import argparse
import logging
import os
import sys
import time

import requests
import setproctitle

import infernoshout

def main():
    logging.basicConfig(level=logging.INFO)

    os.environ["SPT_NOENV"] = "true"
    setproctitle.setproctitle(sys.argv[0])

    parser = argparse.ArgumentParser(description="Command line feed for Inferno Shoutbox")
    parser.add_argument("-b", "--backlog", action="store_true", help="Display the backlog after connecting")
    parser.add_argument("url", help="Base URL of the forum")
    parser.add_argument("cookies", help="Cookies in the standard Cookie header format (RFC 6265, section 4.1.1)")
    args = parser.parse_args()

    s = infernoshout.Shoutbox(args.url, infernoshout.utils.dict_from_cookie_str(args.cookies))

    if args.backlog:
        for i in s.get_new():
            print(i, flush=True)
    else:
        s.initial_fetch()

    while True:
        time.sleep(5)
        try:
            for i in s.get_new():
                print(i, flush=True)
        except requests.exceptions.ConnectionError as e:
            logging.warn("connection error: %s" % e)

if __name__ == "__main__":
   main()
