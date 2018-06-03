
init:
	python3 -m pip install -r requirements.txt -e .

uninstall:
	python3 -m pip uninstall -y image_sorter

.PHONY: init
