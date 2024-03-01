import datetime
import sys

from parsy import regex
from parsy import *
import parsy


## mod lexer

four_digit = parsy.regex(r"[0-9]{4}").map(int)
two_digit = parsy.regex(r"[0-9]{2}").map(int)

dash = string("-")

year = four_digit.desc("4 digit year")
month = two_digit.desc("2 digit month")
day = two_digit.desc("2 digit day")

## mod parser

date = seq(year=year << dash, month=month << dash, day=day)

units = parsy.string_from("days", "weeks", "months", "years")
units_spaced = parsy.whitespace >> units << parsy.whitespace

how_many_until = parsy.seq(
    string("how many") >> units_spaced << string("until"), parsy.whitespace >> date
)

how_long_until = parsy.seq(string("how long until") >> parsy.whitespace >> date)

# query = seq(how_long_until=how_long_until, how_many_until=how_many_until)
query = how_long_until | how_many_until


def parse(target: str, override_present=None):
    tt = target.strip()
    present = datetime.datetime.now()

    try:
        (date,) = how_long_until.parse(tt)
        d = datetime.date(**date)
        return calculate(d)
    except ParseError:
        pass

    try:
        units, date = how_many_until.parse(tt)
        d = datetime.date(**date)
        return calculate(d)
    except ParseError:
        pass

    return "Bad input"


def calculate(date: datetime.date | datetime.datetime):
    if isinstance(date, datetime.date):
        present = datetime.date.today()
    elif isinstance(date, datetime.datetime):
        present = datetime.datetime.now()
    else:
        raise ValueError

    delta = present - date
    delta = abs(delta)
    print(delta)

    num_days = delta.days

    return f"There are {num_days} days between {present} and {date}"
