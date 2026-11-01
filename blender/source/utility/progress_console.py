import os
import sys
import math
import colorama

try:
    os.get_terminal_size()

    _BLOCKS: list['ConsoleLoadBlock'] = []
    _CURRENT_BLOCK: 'ConsoleLoadBlock' = None
    _DISPLAY_WIDTH = 48
    _PREV_LINES_COUNT = 0

    _NAME_TEMPLATE = (
        colorama.Style.BRIGHT
        + colorama.Fore.BLACK
        + "{0}"
        + colorama.Fore.RESET
        + "{1}"
        + colorama.Fore.BLACK
        + "{2}"
        + colorama.Fore.RESET
        + colorama.Style.RESET_ALL
    )

    _BAR_PROGRESS_TEMPLATE = (
        colorama.Fore.GREEN
        + "{0}{1}"
        + colorama.Fore.RESET
        + "{2}"
    )

    _BAR_GOAL_TEMPLATE = (
        colorama.Fore.BLACK
        + colorama.Style.BRIGHT
        + " / "
        + colorama.Style.RESET_ALL
        + colorama.Fore.RESET
        + "{0}"
    )

    _TEXT_TEMPLATE = (
        colorama.Fore.CYAN
        + "{0}"
        + colorama.Fore.BLACK
        + colorama.Style.BRIGHT
        + "..."
        + colorama.Style.RESET_ALL
        + colorama.Fore.RESET
    )


    class ConsoleLoadBlock:

        row: int
        name: str
        progress_goal: int

        current_progress: int
        current_text: str

        _header: str
        _total_bar_width: int

        _current_full_block_count: int
        _current_has_half_block: int

        def __init__(self, row: int, name: str, progress_goal: int):
            self.row = row
            self.name = name
            self.progress_goal = progress_goal
            self.current_progress = 0

            self._header = f" {name} "
            name_length = len(self._header)
            dashes = _DISPLAY_WIDTH - name_length
            if dashes >= 2:
                dash_div = dashes / 2.0
                dashes_left = math.ceil(dash_div)
                dashes_right = math.floor(dash_div)

                self._header = _NAME_TEMPLATE.format(
                    "=" * dashes_left,
                    self._header,
                    "=" * dashes_right
                )

            self._total_bar_width = _DISPLAY_WIDTH - \
                4 - (len(str(progress_goal)) * 2)

            self._current_full_block_count = 0
            self._current_has_half_block = False
            self.current_text = ""

        def _print_bar(self, progress: int, reprint: bool):
            if self.progress_goal <= 0:
                return

            if not reprint and (progress is None or progress == self.current_progress):
                print()
                return

            if progress >= self.progress_goal:
                full_block_count = self._total_bar_width
                has_half_block = False
                remainder = 0

            else:
                block_count = (progress / self.progress_goal) * \
                    self._total_bar_width
                full_block_count = math.floor(block_count)
                has_half_block = (block_count - full_block_count) > 0.5
                remainder = self._total_bar_width - full_block_count

            print_text = ""

            if reprint or self._current_full_block_count != full_block_count or self._current_has_half_block != has_half_block:

                print_text = _BAR_PROGRESS_TEMPLATE.format(
                    "█" * full_block_count,
                    "▌" if has_half_block else " ",
                    " " * remainder
                )

            else:
                print(colorama.Cursor.FORWARD(self._total_bar_width + 1), end="")

            print_text += str(progress).rjust(len(str(self.progress_goal)))

            if reprint:
                print_text += _BAR_GOAL_TEMPLATE.format(self.progress_goal)

            print(print_text)
            self.current_progress = progress
            self._current_full_block_count = full_block_count
            self._current_has_half_block = has_half_block

        def _print_text(self, text: str, reprint: bool):
            if reprint or text != self.current_text:
                print(colorama.ansi.clear_line(), end="")
                print(_TEXT_TEMPLATE.format(text))
                self.current_text = text
            else:
                print()

        def _print(self, text: str, progress: int, reprint: bool):
            self._print_bar(progress, reprint)
            self._print_text(text, reprint)

        def _move_cursor(self, offset):
            print(colorama.Cursor.POS(1, self.row + offset), end="")

        def reprint(self):
            self.print_full(self.current_text, self.current_progress)

        def print_full(self, text: str, progress: int):
            self._move_cursor(0)
            print(self._header)
            self._print(text, progress, True)

        def print_update(self, text: str, progress: int):
            self._move_cursor(1)
            self._print(text, progress, False)

        def clear_below(self, offset: int):
            self._move_cursor(offset)
            print(colorama.ansi.clear_screen(0), end="")


    def _validate_print(block_modif):
        current_lines_count = os.get_terminal_size().lines
        global _PREV_LINES_COUNT

        if _PREV_LINES_COUNT is None or _PREV_LINES_COUNT != current_lines_count:
            _PREV_LINES_COUNT = current_lines_count
            print("\n" * (_PREV_LINES_COUNT + 2))

            for block in (_BLOCKS[:block_modif] if block_modif != 0 else _BLOCKS):
                block.reprint()
            return True

        return False


    def cleanup():
        while len(_BLOCKS) > 0:
            end()


    def start(name: str, progress_limit: int = 0):
        if len(_BLOCKS) == 0:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            colorama.init(autoreset=True)

            global _PREV_LINES_COUNT
            _PREV_LINES_COUNT = None
            _validate_print(0)

        global _CURRENT_BLOCK

        if _CURRENT_BLOCK is not None:
            row = _CURRENT_BLOCK.row + 3
            if _CURRENT_BLOCK.progress_goal > 0:
                row += 1
        else:
            row = 1

        _CURRENT_BLOCK = ConsoleLoadBlock(row, name, progress_limit)
        _BLOCKS.append(_CURRENT_BLOCK)
        _CURRENT_BLOCK.reprint()


    def update(text: str, progress: int | None = None, clear_below: bool = False):
        global _CURRENT_BLOCK
        if _validate_print(-1):
            if progress is None:
                progress = _CURRENT_BLOCK.current_progress
            _CURRENT_BLOCK.print_full(text, progress)
            return

        _CURRENT_BLOCK.print_update(text, progress)

        if clear_below:
            _CURRENT_BLOCK.clear_below(4)


    def end():
        global _CURRENT_BLOCK
        if _CURRENT_BLOCK is None:
            return

        _CURRENT_BLOCK.clear_below(0)
        del _BLOCKS[-1]

        if len(_BLOCKS) == 0:
            colorama.deinit()
            _CURRENT_BLOCK = None
        else:
            _CURRENT_BLOCK = _BLOCKS[-1]

except:
    def _validate_print(block_modif):
        pass

    def cleanup():
        pass

    def start(name: str, progress_limit: int = 0):
        pass

    def update(text: str, progress: int | None = None, clear_below: bool = False):
        pass

    def end():
        pass
