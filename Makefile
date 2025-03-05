.PHONY: isort
isort:
	uv run isort .

.PHONY: black
black:
	uv run black .

.PHONY: flake8
flake8:
	uv run flake8 .


