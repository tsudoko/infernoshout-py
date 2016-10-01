#!/usr/bin/env python3
import argparse
import collections
import datetime
import logging
import os
import re
import sys
import time

import bs4
import requests
import setproctitle

import util


class Shoutbox:
    base_url = ""
    inferno_url = ""
    s = None
    lines = []
    read = collections.deque(maxlen=21)

    def __init__(self, base_url, cookie={}, inferno_path="/infernoshout.php", base_path="/index.php"):
        self.base_url = base_url
        self.inferno_url = self.base_url + inferno_path
        self.s = requests.Session()
        self.s.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": self.base_url + base_path,
        })
        if cookie:
            self.s.cookies.update(cookie)

    def _parse(self, html):
        MAGIC = "<<~!PARSE_SHOUT!~>>"

        try:
            active_users = util.atoi(html)
            logging.info("%d active users" % active_users)
            html = html[len(str(active_users)):]
        except ValueError:
            pass

        if not html.startswith(MAGIC):
            logging.warning("ignoring bogus html: %s" % html)
            return

        html = html.lstrip(MAGIC)
        h = bs4.BeautifulSoup(html)

        # put the full URL after the text inside the "a" tag
        for a in h.find_all("a"):
            if "href" not in a.attrs:
                continue

            if a['href'] == "#":
                continue

            a.string.replace_with("%s (%s)" % (a.string, a['href']))

        for br in h.find_all("br"):
            br.string = "\n"

        chat = h.get_text()

        # remove timestamps - they're relative, and thus they make read lines appear as unread when the day changes
        chat = re.sub("^\[[^\]]*\] ", "", chat, flags=re.MULTILINE)
        return chat

    def _get(self):
        params = {
            "action": "getshouts",
            "timestamp": datetime.datetime.now().strftime("%s200"),
        }

        r = self.s.get(self.inferno_url, params=params)
        return r.text

    def initial_fetch(self):
        self.update()
        for i in self.lines:
            self.read.append(i)
        self.lines = []

    def update(self):
        l = self._parse(self._get()).rstrip("\n").split('\n')
        self.lines.extend(l)

    def get_new(self):
        ret = []
        self.update()

        for i in self.lines:
            if i not in self.read:
                ret.append(i)
                self.read.append(i)
            else:
                logging.debug("skipping line " + i)

        self.lines = []
        return ret

    def send(self, msg):
        params = {
            "action": "newshout"
        }

        s.post(self.inferno_url, params=params, data={"shout": msg})


def main():
    logging.basicConfig(level=logging.INFO)

    os.environ["SPT_NOENV"] = "true"
    setproctitle.setproctitle(sys.argv[0])

    parser = argparse.ArgumentParser(description="Command line feed for Inferno Shoutbox")
    parser.add_argument("-b", "--backlog", action="store_true", help="Display the backlog after connecting")
    parser.add_argument("url", help="Base URL of the forum")
    parser.add_argument("cookies", help="Cookies in the standard Cookie header format (RFC 6265, section 4.1.1)")
    args = parser.parse_args()

    s = Shoutbox(args.url, util.dict_from_cookie_str(args.cookies))

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
