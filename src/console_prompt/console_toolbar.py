class ConsoleToolbar:
    def __init__(self, blocks_x: int, blocks_y: int):
        self.toolbar_state = [("bg:#eeeeee", "")]

        self.toolbar_blocks = [[("", "") for _ in range(blocks_x)] for _ in range(blocks_y)]
        self.needs_updating: bool = False
        self.blocks_x = blocks_x
        self.blocks_y = blocks_y


    def get(self):
        if self.needs_updating:
            self.toolbar_state = []
            for y in range(self.blocks_y):
                self.toolbar_state.extend(horizontally_join(*(self.toolbar_blocks[y]), height=10))
            self.needs_updating = False

        return self.toolbar_state

    def update(self, block_x: int, block_y: int, text: str, style: str = ""):
        self.toolbar_blocks[block_y][block_x] = (style, text)
        self.needs_updating = True



def horizontally_join(*blocks, height:int = 20):
    """
    Requires blocks to have consistent width in every line.
    Blocks can end early, however they must have at least one line, to gauge their width
    every block in blocks: ("text style", text)
    result: [("text style", text), ...]
    """
    result = []
    styles = [style for style, text in blocks]
    lines = [[line for line in text.split("\n")] for style, text in blocks]
    widths = [len(block_lines[0]) * ' ' for block_lines in lines]

    empty_block_ids = []
    for row in range(height):
        for block_i in range(len(blocks)):
            if len(lines[block_i]) <= row:
                # there isn't a line for this row in this block
                # mark it as empty
                empty_block_ids.append(block_i)

            if block_i in empty_block_ids:
                # if it's empty add the appropriate space count with default style
                result.append(("", widths[block_i]))
                continue

            # if len(empty_block_ids) == len(blocks) - 1:
            #     # if there's only one of the blocks left, there is no point sending it in separately styled chunks
            #     result.append(
            #         (styles[block_i],
            #          ),
            #     )
            result.append((styles[block_i], lines[block_i][row]))
        result.append(("", '\n'))

    return result
