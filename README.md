# Progress Quest (Python)

This is a Python-based command-line interface (CLI) reimplementation of [Progress Quest](http://progressquest.com/), an antic and fantastical computer role-playing game.

## Prerequisites

- Python 3.11 (or any reasonably recent version)

## Running the Game

To start the game, run the `main.py` script in your terminal:

```
python3 main.py
```

The game will start and continue progressing automatically.

### Keyboard Quick Reference

- Ctrl+C: Exit **Progress Quest**

### Saving and Loading

- **Automatic Saving**: The game automatically saves your progress to `save.pq` located in the project directory.
- **Backup Save**: A backup save file (`save.pq.bak`) is created every time a new save is generated.
- **Loading**: Upon starting, the game will automatically load from `save.pq`. If no save file is found, the game will begin a new adventure.
- **Corrupted Save**: If the save file is corrupted for any reason, simply delete `save.pq` and the game will restart from the beginning.

## Known Limitations

- Only the "Roll" feature of the character creation form is currently implemented. Other options are not available yet.
- "Unroll" (a feature exclusive to the original **Progress Quest**) is not implemented.
- Some game mechanics may differ or be simplified compared to the original.
    - I know nothing about Pascal, so I made some educated guesses during the development process.
- Multiple save files are not supported. Only one save file (`save.pq`) is maintained at a time.

## License

This project is licensed under the MIT License. See LICENSE.txt for more details.

## Acknowledgements

This project is based on the original [Progress Quest](https://bitbucket.org/grumdrig/pq/) game and its source code. Special thanks to the original creators and contributors for their inspiration and for making this project possible.
