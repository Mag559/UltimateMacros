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

`um.base_macro.BaseMacro` serves as a base class for all other macros,
simplifying the logic to:
*on event caught via _update, if event A, do a, if event B, do b*,
which makes new macros very easy to create.

One of the main features is also the `interpreter_macro`, which can read and realize instructions
written in a text file (by convention .ins), best for relatively simple tasks which can be
broken down into step-by-step instructions with little (interpreting can be paused)
to no human input required. 

`recorder_macro` allows the user to records his/her inputs into a format used by `interpreter_macro`
and therefore skip the tedius part of typing out individual key presses.

For very short and repetitive tasks, such as prefixing variables with 'static final' in java
a combination of the previous two macros can be used. Quickly record the typing
and then repeat the inputs with the press of a button.


## How to run
1. Download the source code: `git clone https://github.com/Mag559/UltimateMacros`
2. Make sure you have python 3.14 available (optionally create a new virtual environment)
3. Download dependencies: `python -m pip install --upgrade pip`, `pip install -e .`

The following has to be done in a terminal (PyCharm and other code editor embedded terminals won't work):
1. Enter the project directory
2. Tell python where the modules are: `$PYTHONPATH=".\src"` (not always required)
3. Run it: `<python> -m um`

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

### Restart
`restart` exits the python process with a special exit code of 10, which can be leveraged
to restart it with an outside script:

```shell
set PYTHONPATH=%PROJECT_DIR%\src
REM alternatively pip install -e <project directory> 

:run_program
"%PYTHON_PATH%" -m um

if %ERRORLEVEL%==10 (
    goto run_program
)
```
where `PYTHON_PATH` is either just `python` or the path to the python executable
of the right virtual environment and `PROJECT_DIR` is the root directory of the project.

## Macro instructions format
Based on the command line instruction format , using `shlex` and `argparse` for the parsing itself.
Most of the default values are stored in the profile, which allows for their easy manipulations
at a cost of a significant dependency.


#### delay
Due to waiting for applications (or OS) to load / register inputs,
various delays are often needed. To make it more convenient,
every instruction can be prefixed with a floating point value,
which will be interpreted as delay in seconds before executing that instruction.

i.e. `0.4 press enter`

If the delay is omitted it's assumed to be 0

#### registers
The "standard" instructions used for detecting images on the screen,
manipulating the mouse and keyboard intentionally constrain their output
to a single flag to better synergize with the jump commands.
This way, no additional commands are needed to convert a variable to
a boolean value accessible to `jump -if`.

Extending this approach to `commands`, however, would encourage
using nonlocal variables in the functions registered to be commands.
A dictionary is therefore maintained by the interpreter
and available to commands through the `--pass_variables` flag.

#### special characters
`---` prefix is used for comments, which must occupy their own line (not after an instruction).
`>` is used for labels, which also can't share a line with an instruction.
For code clarity it is possible to prefix instructions with whitespaces.

#### instruction overview

The full help messages are updated automatically and available in `docs/instructions.md`.

- `press <key>` - press a key on the keyboard
- `release <key>` - release a key on the keyboard
- `tap <key>` - press a key and release a key
- `type <string>` - tap each key corresponding to each letter in the string


- `move <tox> <toy>` - move mouse to absolute coordinates
- `shift <tox> <toy>` - move mouse to relative coordinates
- `click {left | middle | right}` - click mouse button
- `scroll <by_x> <by_y>` - scroll


- `jump` - jump to a different instruction, either by adding a value to the instruction counter
(i.e. `jump -by 1` skips the next instruction)
or going to a label (i.e. `jump -to start` executes the instructions after `> start`)
- `set_flag` - set the flag to true
- `clear_flag` - set the flag to false
- `log <message>` - log the specified message
- `end` - end the interpreting of this script


- `detect <image_path>` - detect the image anywhere on the screen
- `match <image_path>` - match a section of the screen against the image
- `await <image_path>` - wait until the image is present on the screen


- `command <function_name> <arguments>...` - trigger a registered function - command