# Infinite RPG

## Windows

Install Python 3 and enable the option to add Python to PATH. Double-click
`start.bat` to launch the game. The save file is stored beside the game script.

## Android with Termux

1. Install Termux from F-Droid or the official Termux GitHub releases.
2. Open Termux and install Python: `pkg update && pkg install python`.
3. To access shared storage, run `termux-setup-storage` and grant permission.
   Use `cd` to enter this folder, for example:
   `cd ~/storage/shared/Download/Infinite_RPG_bundle`.
4. Launch the game with `python Infinite_RPG.py`.

Use the game's `Q` action to save and exit. Keep `infinite_factions_rpg.json`
beside the script to preserve your save between sessions.
