# Evoland TAS

## Setup

* Run `pip install -r requirements.txt`
* The TAS will use sane defaults, but if required, it's possible to specify run parameters by copying the contents of `config.yaml.example` to `config.yaml` and edit its contents.
* The TAS is intended to be run with Evoland Legendary edition (available on Steam, it combines both Evoland1 and Evoland2 in one game)

## Perform run

* Run `py main.py`
* Navigate the interface using the keyboard. Currently only the Evoland 1 TAS does anything.
* Ensure you are on the "Press any key to start" screen before executing the TAS. Don't have any physical controllers connected.
* By default, a new run will be started (this requires that there is one empty save slot in Evoland)
* It is possible to resume in the middle of a run using checkpoints:
  * Set the `checkpoint` value in `config.yaml` (refer to example file for valid strings) and set `saveslot` to the valid 1-indexed Evoland 1 save that represents this state.
  * Valid saves are provided in the `saves/evo1` folder.
  * The saves need to be copied over to the game save folder and be changed to a name in the range `slot0.sav`-`slot4.sav`.
  * Currently, the TAS behaves incorrectly if all 5 save slots are filled. Please leave the last one open.

## For development

* Run `pip install pre-commit` and `pre-commit install` to install pre-commit hooks.
