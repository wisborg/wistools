"""
Various utilities for manipulating text.
"""

from .basic import iterate


def banner(lines, spacing: int = 5, max_width: int = 0) -> str:
    """Returns a banner with the lines centered inside a frame.
    spacing is the amount of space around the longest line.
    max_width is the maximum width allowed for each line; lines
    longer than max_width as broken into multiple lines."""
    if max_width > 0:
        print_lines = []
        for line in iterate(lines):
            print_lines += split_line_by_length(str(line), max_width)
    else:
        print_lines = [str(line) for line in iterate(lines)]

    long_line = 0
    for line in print_lines:
        long_line = max(long_line, len(line))

    full = '*' * (long_line + 2 * spacing + 2) + '\n'
    sparse = '*' + ' ' * (long_line + 2* spacing) + '*\n'
    fmt = f'*{{:^{long_line + 2 * spacing}s}}*\n'
    output = full + sparse
    for line in print_lines:
        output += fmt.format(line)
    output += sparse + full
    return output


def split_line_by_length(line: str, max_width: int) -> list[str]:
    """Splits a line into multiple lines by restricting each new line
    to a maximum width. Words will not be split, so if a single word
    is longer than max_width, that line will exceed the maximum width
    requested. If max_width <= 0 then the line will not be split."""
    lines = []
    if max_width <= 0 or line.strip() == '':
        lines = [line]
    else:
        words = line.split(' ')
        line_words = []
        cur_width = 0
        for word in words:
            if cur_width == 0 or (cur_width + len(word) + 1) > max_width:
                if cur_width > 0:
                    lines.append(' '.join(line_words))
                line_words = [word]
                cur_width = len(word)
            else:
                line_words.append(word)
                cur_width += len(word) + 1

        if cur_width > 0:
            lines.append(' '.join(line_words))

    return lines
