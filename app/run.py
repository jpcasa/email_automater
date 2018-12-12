import os, json
from classes.automator import Automator

# Clear Screen


def program():
    """Main program."""
    with open('config/config.json') as f:
        auto = Automator(json.load(f))
    auto.program()


if __name__ == '__main__':

    # Run Program
    program()
