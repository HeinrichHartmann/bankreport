install:
	-pip uninstall -y bankreport
	-rm -r dist
	poetry build
	pip install dist/*.whl
	-pyenv rehash

bump:
	poetry version patch
	git commit -am "bump $(poetry version -s)"
	git push

release:
	rm -r dist
	poetry build
	poetry publish
