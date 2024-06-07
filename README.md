# ScoreSensei

## Preview
Home Screen

![homescreen](https://github.com/kitchy115/ScoreSensei/assets/113550578/8cf2886f-3fa0-4255-8dc5-0c7641198d30)

Login

![login](https://github.com/kitchy115/ScoreSensei/assets/113550578/ea7ac7ea-da41-4ea1-991d-d83889786e5d)

User Page

![userpage](https://github.com/kitchy115/ScoreSensei/assets/113550578/5c286645-3868-4237-92d8-b3f037fe0eb1)

Dashboard

![dashboard](https://github.com/kitchy115/ScoreSensei/assets/113550578/7a3b5dbb-9142-48dc-a87c-840bde58694b)

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

```
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

```
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

