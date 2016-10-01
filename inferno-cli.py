#!/usr/bin/env python3
import argparse
import asyncio
import logging
import os
import sys

import requests
import setproctitle

import infernoshout

@asyncio.coroutine
def recv_loop(shoutbox):
    while True:
        yield from asyncio.sleep(5)
        try:
            for i in shoutbox.get_new():
                print(i, flush=True)
        except requests.exceptions.ConnectionError as e:
            logging.warn("connection error: %s" % e)


def handle_input(shoutbox):
    i = sys.stdin.readline().rstrip("\r\n")
    if not i: # EOF
        exit()

    shoutbox.send(i)


def main():
    logging.basicConfig(level=logging.INFO)

    os.environ["SPT_NOENV"] = "true"
    setproctitle.setproctitle(sys.argv[0])

    parser = argparse.ArgumentParser(description="Command line feed for Inferno Shoutbox")
    parser.add_argument("-b", "--backlog", action="store_true", help="Display the backlog after connecting")
    parser.add_argument("-n", "--no-input", action="store_true", help="Disable sending messages via stdin")
    parser.add_argument("url", help="Base URL of the forum")
    parser.add_argument("cookies", help="Cookies in the standard Cookie header format (RFC 6265, section 4.1.1)")
    args = parser.parse_args()

    s = infernoshout.Shoutbox(args.url, infernoshout.utils.dict_from_cookie_str(args.cookies))

    if args.backlog:
        for i in s.get_new():
            print(i, flush=True)
    else:
        s.initial_fetch()

    loop = asyncio.get_event_loop()

    if not args.no_input:
        loop.add_reader(sys.stdin, lambda: handle_input(s))

    loop.run_until_complete(recv_loop(s))

if __name__ == "__main__":
   main()
