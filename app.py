from datecalc import run_application_parser

from fasthtml.common import *

from fasthtml import ft

import json

app, rt = fast_app(
    live=True,
    debug=True,
    pico=False,
    hdrs=(
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
    ),
)


@app.get("/")
def get():
    x = Form(
        Div(
            Label("Enter your query:", _for="query", cls="form-label"),
            Input(type="text", name="query", id="query", cls="form-control"),
            cls="form-group mb-3",
        ),
        Button("Submit", cls="btn btn-primary mb-3"),
        cls="mt-5",
        hx_get="/parse",
        hx_swap="afterend",
    )

    results = Div(Titled('blank'),id="results", cls="border border-primary rounded")

    return Title("mukund"), Div(x, results, cls="container")


@rt("/parse")
def get(query: str):
    resp = run_application_parser(query)

    return ft.Div(
        Titled(query),
        resp,
        hx_swap_oob='true',
        id = 'results',
        cls="border border-primary rounded",
    )


serve()
