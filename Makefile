install:
	rm -r dist
	poetry build
	pip install --force-reinstall dist/*.whl
	pyenv rehash
