python version 3.9.2

# set up environmnet
docker compose up -d (should be ready redis, postgres and api for local tests)

# create virtualenv
> python -m venv url-shortener/venv
> pip install -r requirements.txt
> pip install -r test_requirements.txt

# Run app 
> export PYTHONPATH=.
> source venv/bin/activate
> flask run (5000 port must be running the app at this point)


## How to run tests
    docker compose exec api pytest

# How setup tables locally
```python
docker compose up -d (start postgres db)
ipython 
> from app import app, db
> with app.app_context():
    db.create_all()
```