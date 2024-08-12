from datecalc import run_application_parser
import parsy

from fasthtml.common import *
from fasthtml import ft

from starlette.responses import JSONResponse

import orjson
import json
from dataclasses import dataclass
from pprint import pprint

BOOTSTRAP_HEADERS = [
    ft.Link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css",
        type="text/css",
        _integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH",
        _crossorigin="anonymous",
    ),
    ft.Script(
        src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js",
        _integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz",
        _crossorigin="anonymous",
    ),
]

app, rt = fast_app(
    live=True,
    debug=True,
    pico=False,
    hdrs=(
        ft.Link(
            rel="stylesheet",
            href="/style.css",
            type="text/css",
        ),
        *BOOTSTRAP_HEADERS,
    ),
)


@dataclass(frozen=True)
class HistoryEntry:
    query: str
    failed: bool = False


history: [HistoryEntry] = []


@app.get("/")
def get():
    query_form = Form(
        Div(
            Label("Enter your query:", _for="query", cls="form-label"),
            Input(type="text", name="query", id="query", cls="form-control"),
            cls="form-group mb-3",
        ),
        Button("Submit", cls="btn btn-primary mb-3"),
        cls="mt-5",
        hx_get="/parse",
        hx_swap="beforebegin",
        hx_target="next .history",
    )

    sample_queries = [
        "how long until start of december",
        "bad one",
        "how long since 2000-01-01",
        "apple sauce",
        "another bad one",
    ]
    something = map(parse, sample_queries)

    history_container = Div(
        *something,
        id="history-container container",
    )

    # FIXME:
    # at the moment, we need to separate the latest response of the calculator
    # and the older queries. Two options I can think of:
    #
    # 1) we can either return the same html tag twice, with one using htmx-swap-oob
    # to replace the latest response, OR
    # 2) we can use hx-on::after-swap to dynamically move the element into the
    # later one

    return Title("mukund"), Div(query_form, history_container, cls="container")


@app.get("/parse")
def parse(query: str):
    snippet = Div(cls="history border border-primary rounded")

    try:
        resp = run_application_parser(query)
        delta = resp["result"]["delta"]
        body = f"There are {delta} days between {resp['start_date']} and {resp[ 'end_date' ]}"

        resp_pretty = orjson.dumps(resp).decode()
        snippet = ft.Div(
            H1(query),
            body,
            ft.Div("raw response below:"),
            ft.Code(resp),
            cls="history border border-success border-2 rounded",
        )
    except parsy.ParseError as e:
        snippet = ft.Div(
            H1(query),
            e,
            cls="history border border-danger border-2 rounded",
        )

    return snippet


serve()
