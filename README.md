# Pydmc

Pydmc is a python client library for interacting with the Informatica Intelligent Cloud Services Platform.

## Installation

Coming soon....

## Usage

```python
from pydmc import IICSClient

# Initialize a client object
client = IICSClient(username='<my-idmc-username>', password='<my-idmc-password>')

# Use the client to print the information about the organization
print(client.get_org_details())

# Use the client to list all roles that exist within the organization
print(client.list_roles())
```

**Note that Informatica determines which organization to interact with based on the user account used in authentication.  e.g. if you use a user that exists in the dev organization then all of your api calls will fetch/update information in dev, if using a qa user it will fetch/update qa**

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

#### Branching

pydmc follows [scaled trunk based development](https://trunkbaseddevelopment.com/), when implementing a feature the workflow is to create a short lived feature branch off of main, make the changes, and then open a pull request back into main for review.

#### Package Management

pydmc uses uv for package management, documentation can be found [here](https://docs.astral.sh/uv/), uv replaces the need for pip as well as virtual environments.  Dependencies are managed in a pyproject.toml file rather than a requirements.txt

**Adding a new requirement**
```bash
uv add requests
```

**running tests**
```bash
uv run pytest
```

uv will create and manage a virtual environment for you behind the scenes and will use the virtual environment and all packages installed in it when using the "uv run" command.

#### Style

Pydmc uses the following packages to maintain style and linting

* [black](https://github.com/psf/black) - code formatter
* [isort](https://pycqa.github.io/isort/) - import sorter
* [flake8](https://flake8.pycqa.org/en/latest/) - enforces [pep8](https://peps.python.org/pep-0008/) styleguide in python code

Before making a commit, please be sure to run the following commands to ensure all formatting and style guidelines are being followed

```
make isort
```

```
make black
```

```
make flake8
```
