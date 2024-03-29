from flask import Flask, request, abort, jsonify, render_template

from .main import run_application_parser

app = Flask(__name__, template_folder="./templates")


@app.route("/")
def landing_page():
    return render_template("index.html")


@app.route("/parse", methods=["GET", "POST"])
def parse_endpoint():
    if request.method == "POST":
        query = request.form["query"]
        if not query:
            abort(400, "Missing required form parameter: query")

    elif request.method == "GET":
        query = request.args.get("query")
        if not query:
            abort(400, "Missing required query parameter: query")

    resp = run_application_parser(query)
    return jsonify(resp)


if __name__ == "__main__":
    app.run(debug=True)
