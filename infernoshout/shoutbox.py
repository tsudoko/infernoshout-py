import collections
import datetime
import logging
import re

import bs4
import dateparser
import requests

from . import utils


class Message:
    def __init__(self, _raw="", timestamp=None):
        self.timestamp = timestamp
        self._raw = _raw
    def __eq__(self, other):
        return self.timestamp == other.timestamp and self._raw == other._raw
    def __ne__(self, other):
        return self.timestamp != other.timestamp or self._raw != other._raw
    def __str__(self):
        return self._raw


class Shoutbox:
    def __init__(self, base_url, cookies={}, inferno_path="/infernoshout.php", base_path="/index.php"):
        self.base_url = base_url
        self.inferno_url = self.base_url + inferno_path
        self.active_users = 0
        self.buf = utils.UniqueBuffer(buflen=21)
        self.s = requests.Session()
        self.s.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:51.0) Gecko/20100101 Firefox/51.0",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": self.base_url + base_path,
        })
        if cookies:
            self.s.cookies.update(cookies)

    def _parse(self, html):
        MAGIC = "<<~!PARSE_SHOUT!~>>"
        timestamp_re = re.compile("^\[[^\]]*\] ")

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

        chat = h.get_text().rstrip("\n").split("\n")
        lines = []

        for line in chat:
            ts_match = timestamp_re.match(line)
            ts = None

            if ts_match:
                ts = dateparser.parse(ts_match.group(0))

            lines.append(Message(timestamp=ts, _raw=timestamp_re.sub("", line)))

        return lines

    def _get(self):
        params = {
            "action": "getshouts",
        }

        r = self.s.get(self.inferno_url, params=params)
        return r.text

    def update(self):
        """Download messages and store them in self.buf."""
        l = self._parse(self._get())

        if l is not None:
            self.buf.items.extend(l)

    def send(self, msg):
        """Send a message to the shoutbox."""
        params = {
            "action": "newshout"
        }

        return self.s.post(self.inferno_url, params=params, data={"shout": msg})
