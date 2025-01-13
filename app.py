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
            href="/styles.css",
            type="text/css",
        ),
        *BOOTSTRAP_HEADERS,
    ),
)


@app.get("/")
def get():
    common_cls = "p-4 bg-white rounded-3 border shadow-sm"

    query_form = Form(
        Label("Enter your query:", _for="query", cls="form-label"),
        Input(type="text", name="query", id="query", cls="form-control mb-2"),
        Button("Submit", cls="btn btn-primary w-100 mb-2"),
        cls="form-group",
        hx_get="/parse",
        hx_swap="beforebegin",
        hx_target="next .history",
    )
    answer = Div(id="answer")

    form_container = Div(query_form, answer, cls=f"{common_cls} mb-4")

    sample_queries = [
        "how long until start of december",
        "bad one",
        "how long since 2000-01-01",
        "apple sauce",
        "another bad one",
    ]
    something = [parse(q, swap=False) for q in sample_queries]

    history = Div(
        Div(*something, cls="card-body"),
        id="history-container container",
        cls="card",
    )

    history_container = Div(H2("Query History", cls="pb-2"), history, cls=common_cls)

    main_container = Div(
        Div(form_container, history_container, cls="container"),
        cls="container-fluid",
        style="min-height: 100vh; background-color: #e3f2fd; padding: 20px;",
    )

    # FIXME:
    # at the moment, we need to separate the latest response of the calculator
    # and the older queries. Two options I can think of:
    #
    # 1) we can either return the same html tag twice, with one using htmx-swap-oob
    # to replace the latest response, OR
    # 2) we can use hx-on::after-swap to dynamically move the element into the
    # later one

    return Title("mukund"), main_container


@app.get("/parse")
def parse(query: str, swap: bool = True):
    base_cls = "history card mb-2"
    elements = []

    try:
        resp = run_application_parser(query)
        delta = resp["result"]["delta"]
        body = f"There are {delta} days between {resp['start_date']} and {resp[ 'end_date' ]}"

        resp_pretty = orjson.dumps(resp).decode()
        elements = [
            body,
            ft.Div("raw response below:", cls="mt-4"),
            ft.Code(resp_pretty),
        ]
    except parsy.ParseError as e:
        elements = ["ParseError: {}".format(e)]

    wrapped = Div(H3(query), *elements, cls="card-body")

    if swap:
        ret = Div(wrapped, cls=base_cls), Div(
            elements[0], hx_swap_oob="true", id="answer"
        )
    else:
        ret = Div(wrapped, cls=base_cls)

    return ret


serve()
