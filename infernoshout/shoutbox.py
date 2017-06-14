import collections
import datetime
import logging
import re

import bs4
import requests

from . import utils


class Shoutbox:
    def __init__(self, base_url, cookies={}, inferno_path="/infernoshout.php", base_path="/index.php", ua=None, use_anus=True):
        self.base_url = base_url
        self.inferno_url = self.base_url + inferno_path
        self.active_users = 0
        self.use_anus = use_anus
        self.last_active = 0
        self.buf = utils.UniqueBuffer(capacity=21)
        self.s = requests.Session()
        self.s.headers.update({
            "X-Requested-With": "XMLHttpRequest",
            "Referer": self.base_url + base_path,
        })
        if ua:
            self.s.headers['User-Agent'] = ua
        if cookies:
            self.s.cookies.update(cookies)

    def _parse(self, html):
        MAGIC = "<<~!PARSE_SHOUT!~>>"

        try:
            self.active_users = utils.atoi(html)
            html = html[len(str(self.active_users)):]
        except ValueError:
            pass

        if not html.startswith(MAGIC):
            logging.warning("ignoring bogus html: %s" % html)
            return

        html = html.replace(MAGIC, "", 1)
        h = bs4.BeautifulSoup(html)

        # put the full URL after the text inside the "a" tag
        for a in h.find_all("a"):
            if "href" not in a.attrs:
                continue

            if a['href'] == "#":
                continue

            if a.string != a['href']:
                a.string.replace_with("%s (%s)" % (a.string, a['href']))

        for br in h.find_all("br"):
            br.string = "\n"

        chat = h.get_text()

        # remove timestamps - they're relative, and thus they make read lines appear as unread when the day changes
        chat = re.sub("^\[[^\]]*\] ", "", chat, flags=re.MULTILINE)
        return chat

    def _check_active(self):
        params = {
            "action": "openanus",
        }

        r = self.s.get(self.inferno_url, params=params)
        logging.info("last activity: %s" % r.text)

        try:
            return int(r.text)
        except ValueError:
            logging.warning("ignoring bogus time: %s" % r.text)
            return None

    def _get(self):
        params = {
            "action": "getshouts",
        }

        r = self.s.get(self.inferno_url, params=params)
        return r.text

    def update(self):
        """Download messages and store them in self.buf."""
        if self.use_anus:
            time = self._check_active()
            if time <= self.last_active:
                 return
            else:
               self.last_active = time

            logging.info("getting more")

        l = self._parse(self._get())

        if l is not None:
            l = l.rstrip("\n").split('\n')
            self.buf.items.extend(l)

    def send(self, msg):
        """Send a message to the shoutbox."""
        params = {
            "action": "newshout"
        }

        return self.s.post(self.inferno_url, params=params, data={"shout": msg})
