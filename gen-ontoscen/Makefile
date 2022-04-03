.PHONY: clean setup test
.DEFAULT_GOAL := help

# Variables
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip


# Clean up
clean:
	rm -rf $(VENV)
	rm -rf data/cache.json
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	find . -name '__pycache__' -exec rm -fr {} +
	find . -name '$(VENV)' -exec rm -fr {} +

# Show help
help:
	@echo "———————————————————————————————————————————————————————————————————"
	@echo " Usage: make [options]"
	@echo " Options:"
	@echo "   help:  Show this help message and exit."
	@echo "   setup: Install/update the dependencies in a virtual environment."
	@echo "   test:  Run the tests."
	@echo "   clean: Clean up the project."
	@echo "———————————————————————————————————————————————————————————————————"


# Install dependencies
setup: $(VENV)/bin/activate
$(VENV)/bin/activate: requirements.txt
	@ test -d $(VENV) || python -m venv $(VENV)
	@ $(PYTHON) -m pip install --upgrade pip
	@ $(PIP) install -r requirements.txt

# Run tests
test: test/ setup
	$(PYTHON) -m unittest discover test -b
