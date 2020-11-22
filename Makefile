image:
	docker build . --tag bankreport

run:
	source pyenv/bin/activate && python ./lib/csv_import.py
