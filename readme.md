# Ultimate Macros

A python project intended for writing automation scripts, macros and similar utilities,
which interact with other software via virtual key presses, mouse clicks and screenshots.


## Quick overview

The main entry point makes use of the `prompt_toolkit` library for command line applications, 
which is fully equipped with autocomplete, history and autosuggest.
From there the user can activate a tool of their choosing
fitted with arguments individual for each one.

The activated tools can range from simple and short like
recursively printing the contents of a directory with `view`,
to activating a macro, which listens and reacts to user inputs while running in the background.
A good example of such a macro is `clipboard_macro`, which makes the clipboard act like a stack:
copy puts the copied text on the stack, paste pastes the topmost text and retrieves
the one below to be pasted next.

The project supports two main kinds of automation:
- macros - custom classes derived from BaseMacro -
intended for situations where something should happen
after the user performs a certain action i.e. play the cutting sound when user presses ctrl+X
- (instruction) scripts - written in macro instruction format .ins files,
executed by the InterpreterMacro - intended for long, sequences of actions
with little to no user involvement i.e. clicking through an installation gui (if no quiet terminal option is available)


## How to run
1. Download the source code: `git clone https://github.com/Mag559/UltimateMacros`
or manually download and extract a compressed archive
2. Make sure you have python 3.14 available (optionally create a new virtual environment)
3. Download dependencies: `python -m pip install --upgrade pip`, `pip install -e .`

The following has to be done in a terminal (PyCharm and other code editor embedded terminals won't work):
1. Enter the project directory
2. Tell python where the modules are: `$PYTHONPATH=".\src"` (not always required)
3. Run it: `python -m um`

Common issues:
- `No module named um` - python doesn't know where that module is,
if setting the `PYTHONPATH` environment variable didn't work,
it is possible to run the project with `src` as the current directory (`cd ./src/`).
- Using wrong python version. Ensure `python -v` reports version 3.14 (or higher).
This can be solved in a crude way by replacing python with a path to the right `python.exe` executable
- `prompt_toolkit.output.win32.NoConsoleScreenBufferError: No Windows console found. Are you running cmd.exe?`
console isn't compatible with prompt toolkit, try using cmd or PowerShell instead


## Compatibility
Project has been developed on Windows, however the most important libraries:
`pynput`, `mss` and `prompt_toolkit` are all cross-platform, so while
it isn't likely to work out-of-the-box it should be plausible to get it running.


## Shortcuts

While shortcuts such as copy, paste, cut, select all are detected,
it is useful to have a few shortcuts that don't have an impact on the other applications.
For this project these are:
- `SHORTCUT1` - left alt + `` ` ``
- `SHORTCUT2` - left alt + windows (command)
- `TOGGLE` - num_lock

They are hard coded in `um.base_macro.macro_event_collector.py`,
but it's the only place they are detected (besides unit tests), so changing them there
won't impact the project.


## Persistent elements

The project operates on a few files in the project directory:
- `myapp.log` - logs
- `myapp_meta.log` - trinket keeping track of how many logs were deleted
- `match_failed.png` - screenshot captured upon failing to wait for
an image to appear on the screen (for debugging purposes)
- `profile_files/cookies.txt` - currently only stores the current profile,
but the file format and role may evolve
- `profile_files/history.txt` - last used prompts recorded by `prompt_toolkit`
- `macro_files/*.ins` - intended directory for macro instruction files


- `profile_files/*.json` - profile files

### Profiles
The grand majority of 'magic numbers' are stored in so called 'profiles'.
Their full list, alongside default values is in `um.profiles.profile_reader.py`.
These values can be overridden with profile files in JSON as only compatible types are used.
A rudimentary example of a dev profile is also provided.
Switching between profiles is done at runtime with `profile`, which updates `profile_files/cookies.txt`
and relevant variables. Only a select few properties require a restart of the program to take effect.
