# Course Calendar Generator

A program to add course schedules to a calendar.

This application is not endorsed or supported by Simon Fraser University.

---

## Running The Code

Install `python 3.10.1`.

Download the code and run `pip install -r requirements.txt`.

Add courses to `courses.txt`, following the example format in the file.

Run `python main.py`.

A calendar ics file with be created with the name `courses.ics`, which can be imported into a calendar.

---

## Features

- Asynchronous programming for course data API calls so that the program runs faster.
- Type hinting, checked using `mypy`.
