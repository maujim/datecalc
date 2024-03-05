import datetime
import sys, traceback

from parsy import regex, string_from
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

today_ = string("today").map(lambda x: datetime.date.today())
tomorrow_ = string_from("tomorrow", "tmrw").map(
    lambda x: datetime.date.today() + datetime.timedelta(days=1)
)
yesterday_ = string_from("yesterday", "yest").map(
    lambda x: datetime.date.today() - datetime.timedelta(days=1)
)


@parsy.generate
def date():
    days_ = (today_ | tomorrow_ | yesterday_).tag("days_")
    simple_ = simple_date.tag("simple")

    tag, parsed = yield days_ | simple_
    return parsed


# all the params from the timedelta constructor are supported
# https://docs.python.org/3/library/datetime.html#datetime.timedelta
units = parsy.string_from(
    "days", "seconds", "microseconds", "milliseconds", "minutes", "hours", "weeks"
)


@parsy.generate
def how_long_until_generated():
    yield string_from("how long", "how many days")
    yield parsy.whitespace
    yield string_from("until", "till")
    yield parsy.whitespace
    end_date = yield date

    start_date = datetime.date.today()

    # instead of this assert, maybe we should fail gracefully
    assert start_date <= end_date

    delta = end_date - start_date

    return {
        "start_date": start_date,
        "end_date": end_date,
        "parser": "how long until",
        "result": {
            "delta": delta.days,
        },
    }


@parsy.generate
def how_long_since_generated():
    parsed = yield string("how long since")
    yield parsy.whitespace
    start_date = yield date

    end_date = datetime.date.today()

    # instead of this assert, maybe we should fail gracefully
    assert start_date <= end_date

    delta = end_date - start_date

    return {
        "start_date": start_date,
        "end_date": end_date,
        "parser": "how long since",
        "result": {
            "delta": delta.days,
        },
    }


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


@parsy.generate
def between_generated():
    yield parsy.string_from("how much time", "how long", "how many days")
    yield parsy.whitespace >> string("between") << parsy.whitespace
    start_date = yield date
    yield parsy.whitespace >> string("and") << parsy.whitespace
    end_date = yield date

    # instead of this assert, maybe we should fail gracefully
    assert start_date <= end_date

    delta = end_date - start_date

    return {
        "start_date": start_date,
        "end_date": end_date,
        "parser": "between",
        "result": {
            "delta": delta.days,
        },
    }


def parse(target: str, override_present=None):
    tt = target.strip()
    present = datetime.date.today()

    full = (
        time_before_generated
        | time_after_generated
        | how_long_since_generated
        | how_long_until_generated
        | between_generated
    )
    return full.parse(tt)
