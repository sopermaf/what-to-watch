# configure hooks for pre-commit with git
setup-hooks:
	pre-commit install

run-hooks:
	pre-commit run-hooks --all-files


runserver: # run the development server for testing
	python manage.py runserver

unit-test: # launch unit tests
	pytest

heroku-requirements:
	poetry export --without-hashes > requirements.txt
