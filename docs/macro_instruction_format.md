
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