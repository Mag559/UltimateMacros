## press

```
usage: press [-h] key

press a key on the keyboard

positional arguments:
  key         the key to press

options:
  -h, --help  show this help message and exit

```

## release

```
usage: release [-h] key

release a key on the keyboard

positional arguments:
  key         the key to release

options:
  -h, --help  show this help message and exit

```

## tap

```
usage: tap [-h] [--duration DURATION] key

tap a key on the keyboard

positional arguments:
  key                  the key to tap

options:
  -h, --help           show this help message and exit
  --duration DURATION  how many seconds between press and release

```

## type

```
usage: type [-h] [--duration DURATION] [--delay DELAY] string

type a string on the keyboard

positional arguments:
  string               the string to type

options:
  -h, --help           show this help message and exit
  --duration DURATION  how many seconds between press and release
  --delay DELAY        how many seconds before each press

```

## move

```
usage: move [-h] x y

move the mouse to absolute pixel coordinates

positional arguments:
  x           the x coordinate to move
  y           the y coordinate to move

options:
  -h, --help  show this help message and exit

```

## shift

```
usage: shift [-h] x y

shift the mouse from the current pixel coordinates

positional arguments:
  x           how much too shift on the x axis
  y           how much too shift on the y axis

options:
  -h, --help  show this help message and exit

```

## click

```
usage: click [-h] button

click a mouse button

positional arguments:
  button      the mouse button to click: left, middle or right

options:
  -h, --help  show this help message and exit

```

## scroll

```
usage: scroll [-h] x y

scroll the mouse in undefined units

positional arguments:
  x           how much to scroll horizontally
  y           how much to scroll vertically

options:
  -h, --help  show this help message and exit

```

## jump

```
usage: jump [-h] by

jump to previous or next instruction

positional arguments:
  by          by how much to change the instruction counter on top of the
              default +1 (jump 0 does nothing)

options:
  -h, --help  show this help message and exit

```

## jump_if

```
usage: jump_if [-h] by

jump to previous or next instruction if the flag is set

positional arguments:
  by          by how much to change the instruction counter on top of the
              default +1 (jump 0 does nothing)

options:
  -h, --help  show this help message and exit

```

## jump_if_not

```
usage: jump_if_not [-h] by

jump to previous or next instruction if the flag is NOT set

positional arguments:
  by          by how much to change the instruction counter on top of the
              default +1 (jump 0 does nothing)

options:
  -h, --help  show this help message and exit

```

## set_flag

```
usage: set_flag [-h]

set the flag

options:
  -h, --help  show this help message and exit

```

## clear_flag

```
usage: clear_flag [-h]

clear the flag

options:
  -h, --help  show this help message and exit

```

## log

```
usage: log [-h] [--level LEVEL] message

log the specified message

positional arguments:
  message        the message to log

options:
  -h, --help     show this help message and exit
  --level LEVEL  the logging level in the logging package i.e.: 10 - debug, 20
                 - info, 30 - warning, 40 - error

```

## end

```
usage: end [-h]

end the interpreting

options:
  -h, --help  show this help message and exit

```

## detect

```
usage: detect [-h] [--confidence_required CONFIDENCE_REQUIRED]
              [--section SECTION] [--click CLICK]
              image_path

detect if an image is present anywhere on the screen, raises the flag if it
is, clears if it isn't

positional arguments:
  image_path            path to the image to be detected, relative to
                        reference images

options:
  -h, --help            show this help message and exit
  --confidence_required CONFIDENCE_REQUIRED
                        how closely does the found section need to match the
                        reference image
  --section SECTION     left,top,width,height of the region of the screen to
                        scan
  --click CLICK         whether to and with what button to click the centre of
                        the found image

```

## match

```
usage: match [-h] [--section SECTION] [--click CLICK] image_path

match a specific section of the screen against a reference picture, raises the
flag if it matches, clears if it doesn't

positional arguments:
  image_path         path to the image to be matched, relative to reference
                     images

options:
  -h, --help         show this help message and exit
  --section SECTION  left,top,width,height of the section to match,usually not
                     needed, as this is automatically read from a .txt file
                     with the same name as the image
  --click CLICK      whether to and with what button to click the centre of
                     the found image

```

## await

```
usage: await [-h] [--anywhere] [--section SECTION] [--timeout TIMEOUT]
             [--interval INTERVAL] [--confidence_required CONFIDENCE_REQUIRED]
             [--click CLICK]
             image_path

wait until a reference image appears on the screenand left click it's centre,
raises the flag if successful, clears otherwise

positional arguments:
  image_path            path to the image to be matched, relative to reference
                        images

options:
  -h, --help            show this help message and exit
  --anywhere            should the program only look for the image in the
                        specified section or anywhere on the screen
  --section SECTION     left,top,width,height of the section to match (does
                        work regardless of the anywhere flag)usually not
                        needed, as this is automatically read from a .txt file
                        with the same name as the image
  --timeout TIMEOUT     maximum time in seconds the waiting should take before
                        giving up,does not include the time it takes to
                        perform the checks themselves
  --interval INTERVAL   time in seconds between checks
  --confidence_required CONFIDENCE_REQUIRED
                        only works with the anywhere flag set, confidence
                        required for the check to pass (for a matching a set
                        section, variables in the profile are used, currently
                        with no way to override them here)
  --click CLICK         whether to and with what button to click the centre of
                        the found image

```

## command

```
usage: command [-h] [--clipboard {none,restricted,copy,paste,full}]
               [--clipboard_delay CLIPBOARD_DELAY] [--pass_interpreter]
               [--pass_variables]
               function_name [arguments ...]

Trigger a registered function. The arguments order is as follows: interpreter,
variables_dict, clipboard_contents, arguments

positional arguments:
  function_name         the name of the function to be triggered
  arguments

options:
  -h, --help            show this help message and exit
  --clipboard {none,restricted,copy,paste,full}
                        how to integrate clipboard into the function: none -
                        don't, restricted - supply the current clipboard and
                        set it to function output, copy - press ctrl+c before
                        doing what restricted does, paste - do what restricted
                        does, then press ctrl+v, full - 3 of the above
                        combined.
  --clipboard_delay CLIPBOARD_DELAY
                        time in seconds given for the clipboard to get updated
  --pass_interpreter    whether to pass the interpreter object to the function
  --pass_variables      whether to pass the variables dictionary to the
                        function

```
