# Evoland TAS

## Setup

* Run `pip install -r requirements.txt`
* The TAS will use sane defaults, but if required, it's possible to specify run parameters by copying the contents of `config.yaml.example` to `config.yaml` and edit its contents.

## Perform run

* Run `py main.py`
* Navigate the interface using the keyboard. Currently only the Evoland 1 TAS does anything.
* By default, a new run will be started (this requires that there is one empty save slot in Evoland)
* It is possible to resume in the middle of a run using checkpoints. Set the `checkpoint` value in `config.yaml` (refer to `evo1/checkpoints.py` for valid strings) and set `saveslot` to the valid 1-indexed Evoland 1 save that represents this state.

## For development

* Run `pip install pre-commit` and `pre-commit install` to install pre-commit hooks.
