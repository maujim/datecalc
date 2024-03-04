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

## mod parser

date = seq(year=year << dash, month=month << dash, day=day)

units = parsy.string_from("days", "weeks", "months", "years")
units_spaced = parsy.whitespace >> units << parsy.whitespace

how_many_until = parsy.seq(
    prefix=string("how many days until") << parsy.whitespace, date=date
).tag("how many days until")

how_long_until = parsy.seq(
    prefix=string("how long until") << parsy.whitespace, date=date
).tag("how long until")

how_long_since = parsy.seq(
    prefix=string("how long since") << parsy.whitespace, date=date
).tag("how long since")

full_parser = how_many_until | how_long_until


def parse(target: str, override_present=None):
    tt = target.strip()
    present = datetime.date.today()

    parser_name, parsed = full_parser.parse(tt)
    parsed_date = datetime.date(**parsed["date"])

    if parser_name == "how long since":
        older = parsed_date
        newer = present
    elif parser_name == "how long until":
        older = present
        newer = parsed_date
    else:
        raise ValueError(f"unknown parser : { parser_name }")

    resp = {
        "query": target,
        "parser_used": parser_name,
        "older": older.strftime("%a %d %b %Y"),
        "newer": newer.strftime("%a %d %b %Y"),
        "calculation": days_between(older, newer),
    }

    return resp


def days_between(older: datetime.date, newer: datetime.date):
    if older > newer:
        return {"status": "error", "reason": "wrong order of dates"}

    delta = newer - older
    num_days = delta.days

    return {
        "status": "success",
        "days": num_days,
    }
