# Reference of actions / tools

### Shortcuts recognized by macros

- SHORTCUT1 - left alt + `
- SHORTCUT2 - left alt + windows (command)
- TOGGLE - num_lock

## exit

```
usage: (exit | quit | q)

exit the program

```

Note: the same effect can be achieved with ``alt + ` ``,
which will exit the program after the next prompt finishes

## view

```
usage: view directory

recursively list subdirectories and files in the given directory

positional arguments:
  directory            which directory to view

```

## notepad

```
usage: notepad file

open the given text file in the associated application

positional arguments:
  file                 file with a .txt extension

```

## profile

```
usage: profile [profile_name]

change the profile

positional arguments:
  profile_name         optional name of the profile to change to,
                       if not given reloads the current profile

```

## restart

```
usage: restart

close the program with a special exit code of 10,
which assuming a small outside script detailed in the readme, leads to running it again 

```

## macro clipboard

```
usage: macro clipboard [stack_size]

run the clipboard macro, which allows the user to copy multiple texts
and seamleassly paste them back in the reverse order

positional arguments:
  stack_size           optional number of entries the macro can support,
                       in case of index going out of bounds, it loops

```

Ctrl + c or Ctrl + x to override the next entry in the stack and make it current
Ctrl + v to paste the current clipboard contents, move the current entry to the previous and copy it to clipboard.
3x SHORTCUT1 in quick succession to exit the macro

If the start / end of the list serving as the stack is reached, it loops

## macro recorder

```
usage: macro recorder file_name

record user inputs into the given file in a format that can be replayed by macro interpreter

positional arguments:
  file_name            file to record inputs into, extension will be overriden to .ins

```

TOGGLE to pause recording instructions.
Inputs are still recorded while paused, but they are written as comments in the file
3x SHORTCUT1 in quick succession to exit the macro

## macro interpreter

```
usage: macro interpreter file_name

interpret instructions in the instruction format detailed in the readme from the given file

positional arguments:
  file_name            file to record inputs into, extension will be overriden to .ins

```

TOGGLE to pause execution (after executing the current instruction is done, not immediately)
3x SHORTCUT1 in quick succession to exit the macro

## macro repeater

```
usage: macro repeater

record and play back user inputs,
combine the functionalities of interpreter and recorder macros

```

TOGGLE to pause recording or executing instructions
SHORTCUT1 to start recording or end recording
SHORTCUT2 to start execution of latest instruction set or end it prematurely

Pressing SHORTCUT2 while recording or SHORTCUT1 while interpreting (unless 3x to terminate) does nothing

## macro textmap

```
usage: macro textmap

replace the selected and copied text by the return value of currently connected function
i.e. change it from snake_case to camelCase

```

Ctrl+c the text,
the copied text is processed by the `text_map` function
and pasted in place of the original text.

## screenshot preview

```
usage: tool screenshot_preview

launch a small tkinter window for previewing a screenshot of set size and position
useful for capturing reference images later used as checkpoints in scripts

```

