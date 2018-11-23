# idebt-finance

This is basic API backend for making finance calls and transitions, implementing and imcaplsulating all finance operation and transfer logic

# Installation

The project is made under default `django` framework and `django-rest` extension.

Firstly, clone the project to local folder

```bash
$ git clone git@githib.com:alexanderSvito/idebt-finance.git && cd idebt-finance/
```

## Dependencies

Next you need to set up your local python environment.
We recommend to use `virtualenvwrapper` or distinct docker environment.

```bash
$ pip install -r requirements.txt
```

## Migration

We use postgres as our database, please make sure you have a postgres installed and running on your machine.
Then you can apply all migrations by running.

```bash
./manage.py migrate
```

## Seeds

When not in production you can prepopulate database with some seed data.

```bash
./manage.py seeds
```

## Running

After you have all migrations applied you can run local development server by simple.

```bash
./manage.py runserver
```
