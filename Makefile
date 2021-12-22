install:
	-pip uninstall -y bankreport
	-rm -r dist
	poetry build
	pip install dist/*.whl
	-pyenv rehash


release:
	# Make sure to update version in pyproject.toml first
	poetry publish
