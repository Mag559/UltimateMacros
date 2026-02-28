## Macro instructions format
`[delay] <instruction> arguments`

##### delay
delay is a float in seconds, executed before the instruction,
it can be skipped to have no delay

##### instruction
- press `<key>` - press a key on the keyboard
- release `<key>` - release a key on the keyboard
- tap `<key> <duration>` - press a key, hold it for duration and release it


- move `<tox,toy>` - move mouse to absolute coordinates
- shift `<tox,toy>` - move mouse to relative coordinates
- click `<button as int>` - click mouse button:
left - 1,
middle - 2,
right - 3.

- await `<image path>` - (untested) wait until a section of the screen matches a reference image

TODO instruction for the find functionality
