# Progress Quest: The Python CLI Edition

This is a Python-based command-line interface (CLI) reimplementation of [**Progress Quest**](http://progressquest.com/), an antic and fantastical computer role-playing game.

The goal of this project is to create a portable edition of the original game. At present, it only requires the Python Standard Library. No third-party libraries are needed.

Note that this project is **not** intended to be an exact replica of the original game. However, effort has been made to ensure that the game mechanics are as close as possible to the original. See [Known Limitations](#known-limitations) for more details.

## Prerequisites

- Python 3.11 (or any reasonably recent version)

## Running the Game

Clone the repository or download the source code to a local folder.

To start the game, run the `main.py` script in your terminal:

```
python3 main.py
```

The game will start and continue progressing automatically.

### Keyboard Quick Reference

- Ctrl+C: Exit **Progress Quest**

### Saving and Loading

- **Saving**: The game automatically saves your progress to `save.pq` located in the project directory on a periodic basis.
    - A backup save file (`save.pq.bak`) is created every time a new save is generated.
    - If the save file is corrupted for any reason, simply delete `save.pq` and the game will restart from the beginning.
- **Loading**: Upon starting, the game will automatically load from `save.pq`. If no save file is found, the game will begin a new adventure.

## Known Limitations

- Only the "Roll" feature of the character creation form is currently implemented. Other options are not available yet.
    - In particular, "Unroll" (a feature exclusive to the original **Progress Quest**) is not implemented.
- Some game mechanics may differ or be simplified compared to the original.
    - I know nothing about Pascal, so I made some educated guesses during development.
- Multiple save files are not supported. Only one save file (`save.pq`) is maintained at a time.

## License

This project is licensed under the MIT License. See LICENSE.txt for more details.

## Acknowledgements

This project is based on the original **Progress Quest** game and its [source code](https://bitbucket.org/grumdrig/pq/). Special thanks to the original creators and contributors for their inspiration and for making this project possible.

Some code and ideas are adapted from [**pq-cli**](https://github.com/rr-/pq-cli), another CLI edition of **Progress Quest**.
