>B2 Project - Tasks Manager - Paris-Saclay University - 2024

# TOUDOU. — Tasks Manager

## What is this project about?

This project is about a tasks manager.  
It allows you to create, list, update and delete tasks. It also allows you to mark tasks as done or undone and to import and export tasks to a csv file.

## Installation

Nedd to install : 
- python >= 3.11 (https://www.python.org/)
- pdm (https://pdm-project.org/latest/)
- click >= 8.1.7 (https://click.palletsprojects.com/en/8.0.x/)
- SQLAlchemy >= 2.0.0 (https://www.sqlalchemy.org/)
- Flask >= 3.0.3 (https://flask.palletsprojects.com/en/3.0.x/)

Then run the following command to install the dependencies:
```bash
pdm install
```

## Usage

### Run CLI commands app
```bash
pdm run tasks
```

### Run web app
```bash
pdm run web
```
#### With debug mode

```bash
pdm run webd
```
*OR*
```bash
pdm run flask --app views --debug run
```