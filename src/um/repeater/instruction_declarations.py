from argparse import ArgumentParser


def create_parsers() -> dict[str, ArgumentParser]:
    # ----------------- keyboard -----------------
    press_parser = ArgumentParser("press a key on the keyboard")
    press_parser.add_argument("key", type=str, help="the key to press")

    release_parser = ArgumentParser("release a key on the keyboard")
    release_parser.add_argument("key", type=str, help="the key to release")

    tap_parser = ArgumentParser("tap a key on the keyboard")
    tap_parser.add_argument("key", type=str, help="the key to tap")
    tap_parser.add_argument("--duration", type=str, help="how many seconds between press and release")

    type_parser = ArgumentParser("type a string on the keyboard")
    type_parser.add_argument("string", type=str, help="the string to type")
    type_parser.add_argument("--duration", type=str, help="how many seconds between press and release")
    type_parser.add_argument("--delay", type=str, help="how many seconds between release and the next press")

    # ----------------- mouse -----------------
    move_parser = ArgumentParser("move the mouse to absolute pixel coordinates")
    move_parser.add_argument("x", type=int, help="the x coordinate to move")
    move_parser.add_argument("y", type=int, help="the y coordinate to move")

    shift_parser = ArgumentParser("shift the mouse from the current pixel coordinates")
    shift_parser.add_argument("x", type=int, help="how much too shift on the x axis")
    shift_parser.add_argument("y", type=int, help="how much too shift on the y axis")

    click_parser = ArgumentParser("click a mouse button")
    click_parser.add_argument(
        "button",
        type=int,
        help="the mouse button to click: left - 1, middle - 2, right - 3"
    )

    scroll_parser = ArgumentParser("scroll the mouse in undefined units")
    scroll_parser.add_argument("x", type=int, help="how much to scroll horizontally")
    scroll_parser.add_argument("y", type=int, help="how much to scroll vertically")

    # ----------------- assembly -----------------
    jump_parser = ArgumentParser("jump to previous or next instruction")
    jump_parser.add_argument(
        "by",
        type=int,
        help="by how much to change the instruction counter on top of the default +1 (jump 0 does nothing)"
    )

    conditional_jump_parser = ArgumentParser("jump to previous or next instruction if the flag is set")
    conditional_jump_parser.add_argument(
        "by",
        type=int,
        help="by how much to change the instruction counter on top of the default +1 (jump 0 does nothing)"
    )

    set_flag_parser = ArgumentParser("set the flag")

    clear_flag_parser = ArgumentParser("clear the flag")

    log_parser = ArgumentParser("log the specified message")
    log_parser.add_argument("message", type=str, help="the message to log")
    log_parser.add_argument(
        "--level",
        type=int,
        default="20",
        help="the logging level in the logging package i.e.: 10 - debug, 20 - info, 30 - warning, 40 - error"
    )

    end_parser = ArgumentParser("end the program via SystemExit exception")
    end_parser.add_argument(
        "--code",
        type=int,
        help="exit code, code 10 is reserved as a signal to restart the program and python interpreter with it"
    )

    # ----------------- screen matching -----------------
    detect_parser = ArgumentParser(
        "detect if an image is present on the screen, raises the flag if it is, clears if it isn't"
    )
    detect_parser.add_argument(
        "image_path",
        type=str,
        help="path to the image to be detected, relative to reference images"
    )

    match_parser = ArgumentParser(
        "match a specific section of the screen against a reference picture, "
        "raises the flag if it matches, clears if it doesn't"
    )
    match_parser.add_argument(
        "image_path",
        type=str,
        help="path to the image to be matched, relative to reference images"
    )
    match_parser.add_argument(
        "--section",
        type=str,
        help="left,top,width,height of the section to match,"
             "usually not needed, as this is automatically read from a .txt file with the same name as the image"
    )

    await_parser = ArgumentParser(
        "wait until a reference image appears on the screen, raises the flag if successful, clears otherwise"
    )
    await_parser.add_argument(
        "image_path",
        type=str,
        help="path to the image to be matched, relative to reference images"
    )
    await_parser.add_argument(
        "anywhere",
        type=bool,
        default=False,
        help="should the program only look for the image in the specified section or anywhere on the screen"
    )
    await_parser.add_argument(
        "--section",
        type=str,
        help="left,top,width,height of the section to match,"
             "usually not needed, as this is automatically read from a .txt file with the same name as the image"
    )
    await_parser.add_argument(
        "--timeout",
        type=float,
        help="maximum time in seconds the waiting should take before giving up,"
             "does not include the time it takes to perform the checks themselves"
    )
    await_parser.add_argument(
        "--interval",
        type=float,
        help="time in seconds between checks"
    )
    await_parser.add_argument(
        "--confidence_required",
        type=float,
        help="only works with the anywhere flag set, confidence required for the check to pass"
             " (for a matching a set section, variables in the profile are used,"
             " currently with no way to override them here)"
    )

    # ----------------- other -----------------
    command_parser = ArgumentParser("trigger a registered function")
    command_parser.add_argument(
        "function_name",
        type=str,
        help="the name of the function to be triggered"
    )
    command_parser.add_argument(
        "args",
        type=str,
        nargs="*",
    )
    command_parser.add_argument(
        "--clipboard",
        type=str,
        choices=["none", "restricted", "copy", "paste", "full"],
        default="none",
        help="how to integrate clipboard into the function:\n"
             "- none - don't\n"
             "- restricted - supply the current clipboard as the first argument and set it to function output\n"
             "- copy - press ctrl+c before doing what restricted does\n"
             "- paste - do what restricted does, then press ctrl+v\n"
             "- full - 3 of the above combined"
    )

    return {
        "press": press_parser,
        "release": release_parser,
        "tap": tap_parser,
        "type": type_parser,
        "move": move_parser,
        "shift": shift_parser,
        "click": click_parser,
        "scroll": scroll_parser,
        "jump": jump_parser,
        "jump_if": conditional_jump_parser,
        "set_flag": set_flag_parser,
        "clear_flag": clear_flag_parser,
        "log": log_parser,
        "end": end_parser,
        "detect": detect_parser,
        "match": match_parser,
        "await": await_parser,
        "command": command_parser,
    }
