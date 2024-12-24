



def in_range(x, a, b, strict=False, allow_rev=False):
    if allow_rev:
        a, b = min(a, b), max(a, b)

    if strict:
        return a < x < b
    else:
        return a <= x <= b


def greater_than(x, a, strict=False):
    if strict:
        return x > a
    else:
        return x >= a


def smaller_than(x, a, strict=False):
    if strict:
        return x < a
    else:
        return x <= a
