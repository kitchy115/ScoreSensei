# ScoreSensei

## Requirements

Create a [virtual environment](https://docs.python.org/3/tutorial/venv.html) (optional but recommended).

Install the required Python packages using [pip:](https://pip.pypa.io/en/stable/)

```bash
pip install -r requirements.txt
```

## Environment Variables (optional)

In Django you can configure:
- SECRET_KEY
- ALLOWED_HOSTS
- DEBUG

These are specified in a .env file. By default, ALLOWED_HOSTS is set to localhost and DEBUG is set to false.

Configure your own variables by modifying the provided template named .env.template, and afterwards rename the file to .env.

## Usage

Initialize the database:

```bash
python manage.py migrate
```

```bash
$ python manage.py migrate
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, scores, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK

  ...

  Applying scores.0001_initial... OK
  Applying sessions.0001_initial... OK
```

Run the web application:

```bash
python manage.py runserver
```

```bash
$ python manage.py runserver
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
May 12, 2024 - 22:40:35
Django version 5.0.2, using settings 'scoresensei.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

Access the web application by going to:

```
http://127.0.0.1:8000/
```

