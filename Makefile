install:
	-pip uninstall -y bankreport
	-rm -r dist
	poetry build
	pip install dist/*.whl
	-pyenv rehash
