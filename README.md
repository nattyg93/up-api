# UP API

## Installation

Install the dependencies using [poetry](https://python-poetry.org/): `poetry install`


## Usage

Populate the following environment variables:
* `UP_API_TOKEN_NAT`
* `UP_API_TOKEN_KAIT`

Run the script: `./get_groceries_balance`


## Development
* Be sure to format all code before committing.
  - Ensure the pre-commit git hook is installed
    (within the environment from where git is run):
    - `pre-commit install`
  - Running `git commit` will now cause the pre-commit hook to run
    before committing is possible.
