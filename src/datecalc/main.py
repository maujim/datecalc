import datetime
import logging
import json
import sys, traceback

from dateutil.relativedelta import relativedelta

from parsy import regex, string_from, seq
import parsy

import pytest


## mod lexer

four_digit = parsy.regex(r"[0-9]{4}").map(int)
two_digit = parsy.regex(r"[0-9]{2}").map(int)

dash = parsy.string("-")

year = four_digit.desc("4 digit year")
month = two_digit.desc("2 digit month")
# TODO: make this a flexible unit for encoding the day
day = two_digit.desc("2 digit day")

number = parsy.regex(r"[0-9]+").map(int)

optional_comma_with_optional_space = parsy.regex(r"\s*,").optional()

## mod parser

today_ = string_from("today", "now").map(lambda x: datetime.date.today())

tomorrow_ = string_from("tomorrow", "tmrw").map(
    lambda x: datetime.date.today() + datetime.timedelta(days=1)
)

yesterday_ = string_from("yesterday", "yest").map(
    lambda x: datetime.date.today() - datetime.timedelta(days=1)
)


@parsy.generate
def _date_yyyymmdd():
    x = yield seq(year=year << dash, month=month << dash, day=day).combine_dict(
        datetime.date
    )
    return x


@pytest.mark.parametrize(
    "input_str, expected_date",
    [
        ("2024-02-20", datetime.date(2024, 2, 20)),
        ("2022-10-15", datetime.date(2022, 10, 15)),
        ("2023-04-30", datetime.date(2023, 4, 30)),
        ("2025-07-12", datetime.date(2025, 7, 12)),
        ("2026-12-25", datetime.date(2026, 12, 25)),
    ],
)
def test__date_yyyymmdd(input_str, expected_date):
    assert _date_yyyymmdd.parse(input_str.lower()) == expected_date


@parsy.generate
def _date_ddmmyyyy():
    # dd-mm-yyyy

    x = (
        yield seq(day=day << dash, month=month << dash, year=year)
        .combine_dict(datetime.date)
        .optional()
    )

    if not x:
        # evaluate tlm in a repl to understand how this code works
        tlm = {
            datetime.date(2022, month, 1).strftime("%b").lower(): month
            for month in range(1, 13)
        }
        three_letter_month = (
            string_from(*tlm.keys()).desc("three letter month").map(lambda x: tlm[x])
        )

        lookup_flm = {
            datetime.date(2022, month, 1).strftime("%B").lower(): month
            for month in range(1, 13)
        }
        full_letter_month = (
            string_from(*lookup_flm.keys())
            .desc("full letter month")
            .map(lambda x: lookup_flm[x])
        )

        month2 = month | full_letter_month | three_letter_month
        y = yield seq(
            day=day << parsy.whitespace,
            month=month2 << optional_comma_with_optional_space << parsy.whitespace,
            year=year,
        ).combine_dict(datetime.date)
        return y

    return x


@pytest.mark.parametrize(
    "input_str, expected_date",
    [
        ("20-02-2024", datetime.date(2024, 2, 20)),
        ("15-10-2022", datetime.date(2022, 10, 15)),
        ("30-04-2023", datetime.date(2023, 4, 30)),
        ("12-07-2025", datetime.date(2025, 7, 12)),
        ("25-12-2026", datetime.date(2026, 12, 25)),
        ("20 Feb 2022", datetime.date(2022, 2, 20)),
        ("10 Mar, 2022", datetime.date(2022, 3, 10)),
    ],
)
def test__date_ddmmyyyy(input_str, expected_date):
    assert _date_ddmmyyyy.parse(input_str.lower()) == expected_date


@parsy.generate
def _date_mmddyyyy():
    x = yield (
        seq(month=month << dash, day=day << dash, year=year)
        .combine_dict(datetime.date)
        .optional()
    )

    if not x:
        # evaluate tlm in a repl to understand how this code works
        lookup_tlm = {
            datetime.date(2022, month, 1).strftime("%b").lower(): month
            for month in range(1, 13)
        }
        three_letter_month = (
            string_from(*lookup_tlm.keys())
            .desc("three letter month")
            .map(lambda x: lookup_tlm[x])
        )

        lookup_flm = {
            datetime.date(2022, month, 1).strftime("%B").lower(): month
            for month in range(1, 13)
        }
        full_letter_month = (
            string_from(*lookup_flm.keys())
            .desc("full letter month")
            .map(lambda x: lookup_flm[x])
        )

        month2 = month | full_letter_month | three_letter_month
        y = yield seq(
            month=month2 << parsy.whitespace,
            day=day << optional_comma_with_optional_space << parsy.whitespace,
            year=year,
        ).combine_dict(datetime.date)
        return y

    return x


# Define test cases for the MM-DD-YYYY parser
@pytest.mark.parametrize(
    "input_str, expected_date",
    [
        ("01-15-2022", datetime.date(2022, 1, 15)),
        ("12-25-2023", datetime.date(2023, 12, 25)),
        ("03-07-2024", datetime.date(2024, 3, 7)),
        ("11-30-2025", datetime.date(2025, 11, 30)),
        ("05-01-2026", datetime.date(2026, 5, 1)),
        ("Feb 25, 2022", datetime.date(2022, 2, 25)),
        ("Apr 15 2022", datetime.date(2022, 4, 15)),
        ("April 20, 2022", datetime.date(2022, 4, 20)),
        pytest.param(
            "March 1 2022",
            datetime.date(2022, 3, 1),
            marks=pytest.mark.skip(reason="we don't support single digit days yet"),
        ),
    ],
)
def test__date_mmddyyyy(input_str, expected_date):
    assert _date_mmddyyyy.parse(input_str.lower()) == expected_date


@parsy.generate
def named_date():
    x = yield (today_ | tomorrow_ | yesterday_)
    return x


# Tests for 'date' parser function
@pytest.mark.parametrize(
    "input_str, expected_date",
    [
        ("today", datetime.date.today()),
        ("tomorrow", datetime.date.today() + datetime.timedelta(days=1)),
        ("yesterday", datetime.date.today() - datetime.timedelta(days=1)),
    ],
)
def test_named_date(input_str, expected_date):
    assert named_date.parse(input_str.lower()) == expected_date


def generate_month2():
    tlm = {
        datetime.date(2022, month, 1).strftime("%b").lower(): month
        for month in range(1, 13)
    }
    three_letter_month = (
        string_from(*tlm.keys()).desc("three letter month").map(lambda x: tlm[x])
    )

    lookup_flm = {
        datetime.date(2022, month, 1).strftime("%B").lower(): month
        for month in range(1, 13)
    }
    full_letter_month = (
        string_from(*lookup_flm.keys())
        .desc("full letter month")
        .map(lambda x: lookup_flm[x])
    )

    month2 = month | full_letter_month | three_letter_month
    return month2


@parsy.generate
def informal_date():
    month2 = generate_month2()
    res = yield seq(
        prefix=parsy.string_from("beginning", "start", "end") << parsy.whitespace,
        month=parsy.string("of") >> parsy.whitespace >> month2,
    )

    # NOTE: if you ask for 'end of april' and its currently june 2024
    # should we assume april 2024 or april 2025?
    # atm, we always match to current year

    target_date = datetime.date(
        day=1,
        year=datetime.date.today().year,
        month=res["month"],
    )

    if res["prefix"] == "end":
        return target_date + relativedelta(months=1) + relativedelta(days=-1)

    return target_date


@pytest.mark.parametrize(
    "input_str, expected_date",
    [
        ("end of april", datetime.date(2024, 4, 30)),
        ("beginning of november", datetime.date(2024, 11, 1)),
        ("end of feb", datetime.date(2024, 2, 29)),
        ("start of july", datetime.date(2024, 7, 1)),
    ],
)
def test_informal_date(input_str, expected_date):
    assert informal_date.parse(input_str.lower()) == expected_date


@parsy.generate
def date():
    date_final_final_v3 = (
        named_date
        | _date_yyyymmdd.desc("yyyy-mm-dd")
        | _date_ddmmyyyy.desc("dd-mm-yyyy")
        | _date_mmddyyyy.desc("mm-dd-yyyy")
        | informal_date
    )

    parsed = yield date_final_final_v3.desc("one of the supported date formats")
    return parsed


# OLD: the params from the timedelta constructor are supported
# https://docs.python.org/3/library/datetime.html#datetime.timedelta

# NEW: all the params from the relativedelta constructor are supported
# https://dateutil.readthedocs.io/en/latest/relativedelta.html#dateutil.relativedelta.relativedelta


@parsy.generate
def units():
    plural_units = [
        "days",
        "seconds",
        "microseconds",
        "milliseconds",
        "minutes",
        "hours",
        "weeks",
        "years",
        "months",
    ]
    singular_units = [plural[:-1] for plural in plural_units]

    # mapping should contain 'day':'days' and 'days':'days'
    lookup = {plural: plural for plural in plural_units}
    lookup.update(dict(zip(singular_units, plural_units)))

    x = yield string_from(*plural_units, *singular_units).map(lambda x: lookup[x])
    return x


@parsy.generate
def how_long_until_generated():
    yield string_from("how long", "how many days")
    yield parsy.whitespace
    yield string_from("until", "till")
    yield parsy.whitespace
    end_date = yield date

    start_date = datetime.date.today()

    if start_date > end_date:
        raise ValueError("start date should be smaller than end date")

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
    parsed = yield parsy.string("how long since")
    yield parsy.whitespace
    start_date = yield date

    end_date = datetime.date.today()

    if start_date > end_date:
        raise ValueError("start date should be smaller than end date")

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

    end_date = start_date + relativedelta(**params)
    delta = end_date - start_date

    return {
        "start_date": start_date,
        "delta": delta.days,
        "parser": tag,
        "result": {
            "end_date": end_date,
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
    end_date = parsed["date"]

    params = {parsed["units"]: parsed["num"]}

    start_date = end_date - relativedelta(**params)
    delta = end_date - start_date

    return {
        "end_date": end_date,
        "delta": delta.days,
        "parser": tag,
        "result": {
            "start_date": start_date,
        },
    }


@parsy.generate
def between_generated():
    yield parsy.string_from("how much time", "how long", "how many days")
    yield parsy.whitespace >> parsy.string("between") << parsy.whitespace
    start_date = yield date
    yield parsy.whitespace >> parsy.string("and") << parsy.whitespace
    end_date = yield date

    if start_date > end_date:
        raise ValueError("start date should be smaller than end date")

    delta = end_date - start_date

    return {
        "start_date": start_date,
        "end_date": end_date,
        "parser": "between",
        "result": {
            "delta": delta.days,
        },
    }


def run_application_parser(target: str, override_present=None):
    target = target.lower().strip()
    present = datetime.date.today()

    full = (
        time_before_generated
        | time_after_generated
        | how_long_since_generated
        | how_long_until_generated
        | between_generated
    )
    resp = full.parse(target)

    return resp


# ======= TESTS =======
