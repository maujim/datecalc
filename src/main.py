import datetime
import sys, traceback

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

number = regex(r"[0-9]+").map(int)

## mod parser

simple_date = seq(year=year << dash, month=month << dash, day=day).combine_dict(
    datetime.date
)


@parsy.generate
def date():
    zz = simple_date.tag("simple")

    tag, parsed = yield zz
    return parsed


# all the params from the timedelta constructor are supported
# https://docs.python.org/3/library/datetime.html#datetime.timedelta
units = parsy.string_from(
    "days", "seconds", "microseconds", "milliseconds", "minutes", "hours", "weeks"
)

how_many_until = parsy.seq(
    prefix=string("how many days until") << parsy.whitespace, date=date
).tag("how many days until")

how_long_until = parsy.seq(
    prefix=string("how long until") << parsy.whitespace, date=date
).tag("how long until")

how_long_since = parsy.seq(
    prefix=string("how long since") << parsy.whitespace, date=date
).tag("how long since")

time_after = parsy.seq(
    num=number << parsy.whitespace,
    units=units << parsy.whitespace << string_from("after", "from") << parsy.whitespace,
    date=date,
).tag("time after")


@parsy.generate
def time_after_generated():
    tag, parsed = yield time_after
    start_date = parsed["date"]

    params = {parsed["units"]: parsed["num"]}
    delta = datetime.timedelta(**params)

    return {
        "start_date": start_date,
        "delta": parsed["num"],
        "parser": tag,
        "result": {
            "end_date": start_date + delta,
        },
    }


time_before = parsy.seq(
    num=number << parsy.whitespace,
    units=units << parsy.whitespace << string_from("before", "to") << parsy.whitespace,
    date=date,
).tag("time before")


@parsy.generate
def time_before_generated():
    tag, parsed = yield time_before
    start_date = parsed["date"]

    params = {parsed["units"]: parsed["num"]}
    delta = datetime.timedelta(**params)

    return {
        "start_date": start_date,
        "delta": parsed["num"],
        "parser": tag,
        "result": {
            "end_date": start_date - delta,
        },
    }


between_prefix = (
    parsy.string_from("how much time", "how long", "how many days")
    << parsy.whitespace
    << string("between")
    << parsy.whitespace
)
between = parsy.seq(prefix=between_prefix, date=date).tag("between")


@parsy.generate
def between_generated():
    raise UnimplementedError

def parse(target: str, override_present=None):
    tt = target.strip()
    present = datetime.date.today()

    try:
        full = time_before_generated | time_after_generated
        return full.parse(tt)
    except ParseError as err:
        pass

    parser_name, parsed = date_comparison_parsers.parse(tt)

    # based on the parser used, we try to get the user intent
    # and we set older and newer accordingly
    #
    # days_between expects older and newer passed in the right order
    # so a failure there means we decoded the intent incorrectly
    if parser_name == "how long since":
        older = parsed["date"]
        newer = present
    elif parser_name == "how long until":
        older = present
        newer = parsed["date"]
    else:
        return {"query": target, "unknown parser": parser_name}

    resp = {
        "query": target,
        "parser_used": parser_name,
        "older": older.strftime("%a %d %b %Y"),
        "newer": newer.strftime("%a %d %b %Y"),
        "calculation": days_between(older, newer),
    }

    return resp
