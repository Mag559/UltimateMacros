# What part of the project does what
Rough overview of what each of the subpackages do.
## um.profiles

#### directories_manager.py
Keep track of paths relevant for the application i.e. `macro_files` directory, `profile_files` directory.

#### profile_reader.py
Store default and load profile settings from JSON files.
Profile settings control nearly all magic numbers in the project,
no care has been taken to validate their overrides, and therefore
it is the users responsibility to not set a negative delay,
random string ment for styling the terminal window e.t.c.

## um.helper_classes
Self-contained helper classes not strongly coupled with other sections of the project.

## um.base_macro
#### input_collector.py
Collect inputs from keyboard and mouse via the pynput library
and propagate that information to subscribers - usually MacroEventCollector

#### input_presser.py
Simulate keyboard and mouse inputs via the pynput library.
Operating system does differentiate them from *true* inputs performed by the user,
however should be treated with care regardless.
These inputs are also detected by the InputCollector class.

#### macro_event_collector.py
Listen to raw inputs collected by InputCollector and process them into ImportantEvents
like copy, paste, cut, double click, right click and so on.

#### base_macro.py
Serves as a base class for all other macros. Handles listening to a MacroEventCollector,
status window, macro timeout (by default after 5 min).
Simplifies the macro logic to:
*on event caught via _update, if event "A", do "a", if event "B", do "b"*,
which makes new macros very easy to create.

#### termination_detector.py
Small class, to which BaseMacro delegates the logic
for detecting multiple same inputs in a short space of time.
Specifically the SHORTCUT1, used 3 times to terminate the macro.

#### status_window.py
Vibe coded tkinter window providing feedback to the user:
what macro is running, what state it's in - running, paused, what mode
and optionally extra details i.e. current clipboard content or executed instruction.

## um.macros
Package with usable macros. Covered both in `docs/actions.md` and their docstring.

## um.screen_match
#### capturer.py
Capture a section of the screen via the mss library.

#### matcher.py
Take two images - typically a reference and a section of the screen
and decide if they match.

#### screen_match.py
Amalgamation of the two above, realizes operations such as:
finding an image on the screen, waiting for a section of the screen to look
similar to a reference image - typically used for waiting
for sth that can vastly different times like an application loading,
a webpage loading e.t.c.

## um.repeater
Package centered around representing the inputs in the macro instruction format.

#### base_interpreter.py
Declare classes and exceptions used by the Interpreter, in a separate module to avoid circular imports.

#### instruction_declarations.py
Definitions of all instructions in the macro instruction format using argparse.
Automatically updated help messages are available in `docs/instructions.md`

#### registered_functions.py
To not bloat the set of supported instructions, less common functionality
is available through commands - functions called by the interpreter.

#### interpreter.py
Parse and execute instructions in the macro instruction format.

#### interpreter_macro.py
Oversee an Interpreter instance allowing for pausing and termination.

#### recorder.py
Record user inputs and convert them into macro instruction format.
Useful to record a section of the script instead of typing it all out by hand,
although the current implementation is basic and doesn't utilize more complex instructions
like `tap --with_ctrl`

#### recorder_macro.py
Much like with the InterpreterMacro, oversee a Recorder instance
commenting out the inputs when it's paused and allowing for termination.

#### repeater_macro.py
Amalgamation of the interpreter and recorder macros.
One macro to both record a series of inputs and play it back.
For very short and repetitive tasks, such as prefixing variables with 'static final' in java.

## um.tools
Package for tools loosely connected to the project, but still helpful for creating
instruction scripts for example.
Currently populated only by ScreenshotPreview, which takes a reference picture
of a section of the screen, to be later used in instruction scripts.

## um.console_prompt
A slight mess of running all the different functionalities of the project,
cool animations and using prompt toolkit.

#### penrose_drawer.py
Draws a spinny penrose triangle with ascii characters: `.`, `*` and `#`.

#### console_drawer.py
Periodically asks PenroseDrawer for a new frame of the animation,
works with ConsoleToolbar to make it colourful and draw it in the terminal.

#### numpy_printer.py
Print lines of text into a form that can be displayed in the ConsoleToolbar.

#### path_completer.py
Custom autocompleter for paths.

#### console_toolbar.py
Manage drawing on the bottom toolbar of the terminal window.

#### console_time_keeper.py
Keep track of time passing and animation being paused,
so it resumes without a jump.

#### console_base.py
A collection of callables and objects useful to action declarations.

#### macro.py, tool.py, miscellaneous.py
Declarations of actions - possible prompts - that can be triggered by the user
to access the functionalities of the project.

#### console_main.py
Messy main class called by `__main__.py` that ties this whole package together.