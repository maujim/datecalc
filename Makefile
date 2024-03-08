run:
	./venv/bin/flask --app src/datecalc/app --debug run --port 8888

venv:
	python3.11 -m venv venv
	./venv/bin/pip3 install -U pip
	./venv/bin/pip3 install -r requirements.txt

test:
	./venv/bin/pytest src/datecalc/main.py
