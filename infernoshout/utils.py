import collections
import http.cookies
import logging

class UniqueBuffer:
    """A simple deduplicating buffer. To add new items, manipulate self.items.
    The actual buffer is not limited in length, the `buflen` argument is used
    to specify the amount of items guaranteed to be unique."""

    def __init__(self, buflen):
        self.items = []
        self.old = collections.deque(maxlen=buflen)

    def pop_all(self):
        """Return all items and remove them from the buffer."""
        ret = []

        for i in self.items:
            if i not in self.old:
                ret.append(i)
                self.old.append(i)

        self.items = []
        return ret


def atoi(string):
    s = []
    for i in string:
        try:
            int(i)
            s.append(i)
        except ValueError:
            break

    return int(''.join(s))


def dict_from_cookie_str(cookie_str):
    c = http.cookies.SimpleCookie()
    d = dict()

    c.load(cookie_str)
    for k, m in c.items():
        d[k] = m.value

    return d
