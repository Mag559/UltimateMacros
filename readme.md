## Project guidelines
- use logging from the `logging` library via `getLogger(__name__)`
- class constructors should initialize classes,
which should only start after calling the `start` or `run` method
- end of `start` method execution should mean all threads started by that class
have been joined
- `run` should not block further code execution
- `stop` method should terminate all threads managed by that class


## SHORTCUTS
- `SHORTCUT1` - left alt + `` ` ``
- `SHORTCUT2` - left alt + windows
- `TOGGLE` - num_lock


## Macro instructions format
Based on the command line instruction format
using `shlex` and `argparse` for the parsing itself.

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
a boolean value accessible to `jump_if`.

Extending this approach to `commands`, however, would encourage
using nonlocal variables in the functions registered to be commands.
A dictionary is therefore maintained by the interpreter
and available to commands through the `--pass_variables` flag.

#### instruction overview
#TODO The full help messages will be available somewhere else

- `press <key>` - press a key on the keyboard
- `release <key>` - release a key on the keyboard
- `tap <key>` - press a key and release a key
- `type <string>` - tap each key corresponding to each letter in the string


- `move <tox> <toy>` - move mouse to absolute coordinates
- `shift <tox> <toy>` - move mouse to relative coordinates
- `click {left | middle | right}` - click mouse button
- `scroll <by_x> <by_y>` - scroll


- `jump <by>` - change instruction counter on top of the +1
- `jump_if <by>` - change instruction counter on top of the +1 if the flag is set
- `jump_if_not <by>` - change instruction counter on top of the +1 if the flag is NOT set
- `set_flag` - set the flag to true
- `clear_flag` - set the flag to false
- `log <message>` - log the specified message
- `end` - end the interpreting of this script


- `detect <image_path>` - detect the image anywhere on the screen
- `match <image_path>` - match a section of the screen against the image
- `await <image_path>` - wait until the image is present on the screen


- `command <function_name> <arguments>...` - trigger a registered function - command