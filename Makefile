migrate:
	@alembic upgrade head

upmain:
	@alembic upgrade head
	@echo "starting"
	@gunicorn app:main -w 1 -b 0.0.0.0:8000 

uptodo:
	@gunicorn app:todo -w 1 -b 0.0.0.0:8001 

upcelery:
	@python app/tasks.py

format:
	@black .
