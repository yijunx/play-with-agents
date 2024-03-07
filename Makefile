migrate:
	@alembic upgrade head

up:
	@alembic upgrade head
	@echo "starting"
	@gunicorn app.main:app -w 3 -b 0.0.0.0:8000 

upcelery:
	@python app/tasks.py

format:
	@black .
