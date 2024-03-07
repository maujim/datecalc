import datetime

from parsy import generate, regex, string, any_char


@generate
def date():
    """
    Parse a date in the format YYYY-MM-DD
    """

    year = yield regex("[0-9]{4}").map(int)
    yield string("-")
    month = yield regex("[0-9]{2}").map(int)
    yield string("-")
    day = yield regex("[0-9]{2}").map(int)

    return datetime.date(year, month, day)


@generate
def hollerith():
    num = yield regex(r"[0-9]+").map(int)
    yield string("H")
    return any_char.times(num).concat()


@generate
def full():
    yield string("how many")
    num = yield regex(r"[0-9]+").map(int)
    yield string("H")
    return any_char.times(num).concat()


query = "how many weeks until April 30, 2035"
