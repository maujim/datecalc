run:
	./venv/bin/ipython -i ./src/main.py

venv:
	python3.11 -m venv venv
	./venv/bin/pip3 install -U pip
	./venv/bin/pip3 install -r requirements.txt

save-requirements:
	./venv/bin/pip3 freeze > requirements.txt

test:
	./venv/bin/python ./src/main.py test