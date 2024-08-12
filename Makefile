run:
	./venv/bin/pip3 install --editable . && \
		./venv/bin/python3 app.py

venv:
	python3.11 -m venv venv
	./venv/bin/pip3 install -U pip
	./venv/bin/pip3 install -r requirements.txt

test:
	./venv/bin/pytest src/datecalc/main.py
