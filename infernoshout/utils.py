import http.cookies


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
