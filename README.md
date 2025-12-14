# SWD Django Demo 
The project can be used as a reference for the SWD lab course.
This project consists of several apps with a focus on loose coupling and dependency injection.
A good article about separation of concerns in Django projects can be found `https://emcarrio.medium.com/business-logic-in-a-django-project-a25abc64718c`.
Good Django tutorials can be found `https://www.djangoproject.com/start/` or `https://cs50.harvard.edu/web/2020/weeks/3/`.

## 1. Requirements

### 1.1 Shell for CLI workflow
Software development needs to interact with the system. Therefor we will encounter an number of CLI (command line interface) tools. To do this effectively we need to use a shell.

In a **Unix-like environments** like Mac/Linux typically a good shell is available out of the box (bash, zsh) in combination with a terminal (terminal, iTerm, Konsole, gnome-terminal, ...). 

For **Windows** a good combination of shell/terminal is [PowerShell](https://github.com/PowerShell/PowerShell)/[Windows Terminal](https://learn.microsoft.com/en-us/windows/terminal/). 


**HINT / Powershell**: For windows users it is quite helpful to set the execution-policy for powershell:
```bash
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```
**HINT / Windows**:  When you want to execute python in a `shell` and the Windows App-Store opens, you need to deactivate this Windows-Behavior: https://stackoverflow.com/questions/58754860/cmd-opens-windows-store-when-i-type-python

### 1.2 Python
For this example the most recent python version is used https://peps.python.org/pep-0719/

- `python 3.13.x` 

To install python itself and as a python package manager we are using the tool [uv - 'An extremely fast Python package and project manager, written in Rust.'](https://docs.astral.sh/uv/)

- **uv install**: Easy via shell/cli: https://docs.astral.sh/uv/getting-started/installation/
- **uv/python version:** It can be used to install the needed python version quite easily: https://docs.astral.sh/uv/concepts/python-versions/


## 2. Development
Best practice for any python development is to start with a virtual environment. This approach and workflow is already integrated into [uv - Project Environment](https://docs.astral.sh/uv/concepts/projects/layout/#the-project-environment)


### 2.1 Usage

1. Install dependencies with the projects main directory: `uv sync`.
2. Activate the virtual environment: `source .venv/bin/activate` / `./.venv/Scripts/activate.ps1`
3. Create the database tables: `uv run python manage.py migrate`
4. Create an admin user: `uv run python manage.py createsuperuser`
5. Run unit tests: `uv run python manage.py test -v 2`
6. Run the development server: `uv run python manage.py runserver`.
7. Open the website in your browser: `http://localhost:8000/admin`.

Or if you want to start with a fresh Django project from scratch:

1. Initialize a new project: `uv init --python 3.13`.
2. Add Django: `uv add Django`
3. Install dependencies with the projects main directory: `uv sync`.
4. Activate the virtual environment: `source .venv/bin/activate` / `./.venv/Scripts/activate.ps1`
5. Create a new Django project: `uv run django-admin startproject django_project .`
6. Add Django applications: `uv run manage.py startapp app_name`


**HINT / Windows**: A realtime virus scanning engine like [Windows Defender](https://www.microsoft.com/en-us/windows/comprehensive-security?r=1) sometimes gets in the way during development. As a result common development actions (compilation, execution of scripts, ..) take ages. To speed up the process it can make sense to disable realtime-scanning during compilation or exclude paths in the scan engine (be aware that this has a security impact!)

- [Deactivate Real-Time Scanning](https://support.microsoft.com/en-us/windows/turn-off-defender-antivirus-protection-in-windows-security-99e6004f-c54c-8509-773c-a4d776b77960)
- [Exclude Folder for Scanning](https://support.microsoft.com/en-us/windows/add-an-exclusion-to-windows-security-811816c0-4dfd-af4a-47e4-c301afe13b26)

### 2.2 IDE
There are a number of IDEs available for python development. You can choose between different variants like [VSCode](https://code.visualstudio.com/), [PyCharm](https://www.jetbrains.com/pycharm/), [VIM](https://realpython.com/vim-and-python-a-match-made-in-heaven/), ...

#### 2.2.1 VSCode
This repository provides a VSCode example setup. It also provides recommendations for extensions which can be installed to have a good development experience (`.vscode/extensions.json`). Unit-testing works and is configured in `.vscode/settings.json` as well as launch/debug capabilities of the Django application in `.vscode/launch.json`.

#### 2.2.2 PyCharm
If you are using pycharm, make sure to have the latest 2025 version installed, otherwise debugging won't be possible.
- first create the venv using (main project folder) `uv sync`
- PyCharm: Settings->Python->Interpreter->Add Interpreter: Add Local Interpreter: 
  - Select existing
  - type: uv
  - point ENV to your ProjectDir/.venv/bin/python 

### 2.3 Dependency Injection
A very often used concept in software-design is **dependency injection** (or inversion of control). A very, very good intro-video regarding DI (dependency injection) can be found on *youtube*, ["Dependency Injection, The Best Pattern"](https://www.youtube.com/embed/J1f5b4vcxCQ?si=Qb4pFAWWazOvzPjm). 
For `Django projects`initialization code is needed to work with the package [*dependency-injector*](https://pypi.org/project/dependency-injector/) --> https://python-dependency-injector.ets-labs.org/examples/django.html

## 3. PortugueseParking – Project Overview

**PortugueseParking** is a Django-based parking management system implementing the following use cases:

* **UC1 – Purchase Season Ticket**
* **UC2 – Entry / Exit with Season Ticket**
* **UC3 – Occasional Parking (Single-use tickets)**

The system follows a **layered architecture**:

* **UI Layer**: Django views and templates
* **Business Logic**: Service layer (`TicketService`, `SlotService`)
* **Persistence**: Django ORM
* **Infrastructure**: PricingService, PaymentService

All use cases are fully implemented, tested, and accessible through the UI.



## 4. Login Credentials (Test User)

```
Username: demo
Password: demo123
```



## 5. Test Data Included

The database is intentionally pre-populated to allow immediate testing.

### Parking Structure

* Areas: Baixa de Lisboa, Lisboa Norte
* Slot Types: SIMPLE, EXTENDED, OVERSIZE
* Accessible and non-accessible slots
* Entry and exit gates per area

### Vehicles

* `11-AA-11`
* `22-BB-22`
* `33-CC-33` (disability permit)

### Active Season Ticket

* Vehicle: `11-AA-11`
* Valid for current period
  This allows direct testing of UC2 without setup.


## 6. How to Test Each Use Case

### UC1 – Purchase Season Ticket

```
/contracts/season/new/
```

Steps:

1. Select vehicle
2. Select period
3. Choose compatible slot
4. Preview price
5. Confirm purchase


### UC2 – Entry / Exit with Season Ticket

Entry:

```
/contracts/gate/entry/
```

Exit:

```
/contracts/gate/exit/
```


### UC3 – Occasional Parking

Entry:

```
/contracts/gate/occasional/entry/
```

Cash Device:

```
/contracts/occasional/cash/
```

Exit:

```
/contracts/gate/occasional/exit/
```



## 7. Testing Strategy

### Unit Tests (Service Layer)

* UC1, UC2, UC3 business logic
* ORM, pricing and payment mocked
* No database dependency

### UI Tests (Views)

* Django test client
* Services mocked
* Template rendering and form behavior verified

This fulfills the assignment requirement for **isolated UI tests**.



## 8. Project Structure

```
PortugueseParking/
├── contracts/        # Tickets, contracts, movements, services, tests
├── parking/          # Areas, slots, gates, pricing, statistics
├── vehicles/         # Vehicle domain
├── customers/        # Authentication and users
├── swd_django_demo/  # Django project configuration
├── db.sqlite3        # Pre-filled test database
├── README.md
```



## 9. Final Remarks

This repository represents a **complete, testable, and demonstrable prototype**, aligned with:

* UML models
* Functional requirements
* Software architecture principles
* Assignment specifications

The project is ready for:

* evaluation
* live demonstration
* screencast recording


## Note
To view a walk throught of the application go to: https://youtu.be/2o_6T_fGMeQ 