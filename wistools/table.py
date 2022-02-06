"""
Tools for working with table outputs.
"""
from collections import namedtuple
import re

FORMATS = namedtuple('TableFormats', ['header', 'row', 'bar'])


class Table(object):
    """Class for building up a table and generate it.
    The formats are in the format used by the .format() string method,
    but with the width removed. For example: >s for a right aligned
    string, <.10s for a string that is truncated at 10 characters,
    and .2f for a currency."""
    _headers: list = []
    _formats: list = []
    _rows: list = []
    _column_widths: list = []

    def __init__(self, headers: list, formats: list or None = None):
        self._headers = headers
        self._rows = []
        self._column_widths = []
        self._ini_column_widths()

        if formats is None:
            self._formats = ['s' for _ in self._headers]
        else:
            if len(headers) != len(formats):
                raise ValueError('The number of formats must match the ' +
                                 'number of headers')

            self._formats = formats

    @property
    def headers(self) -> list:
        """Return the table headers."""
        return self._headers

    @property
    def rows(self) -> list[list]:
        """Return the current rows in the table as list (rows) of
        lists (columns)."""
        return self._rows

    @rows.setter
    def rows(self, rows: list[list]):
        """Initialise the table with a list of rows with each row being
        itself a list of columns."""
        self._rows = []
        self._ini_column_widths()
        self.add_rows(rows)

    def formats(self, frame: bool = False, spacing: int = 3) -> FORMATS:
        """Returns the format definitions for the table as a FORMATS
        named tuple. This is useful for implementing custom generators.
        """
        bar = ''
        fmt_header = ''
        fmt_row = ''
        i = 0
        for width in self._column_widths:
            if frame:
                bar += '+-' + ('-' * width)
                fmt_header += '| '
                fmt_row += '| '
            else:
                bar += '-' * width
                if i > 0:
                    bar += '-' * spacing
                    fmt_header += ' ' * spacing
                    fmt_row += ' ' * spacing

            fmt_header += f'{{{i}:<{width}s}}'
            fmt_col = self._fmt_col(i, width)
            fmt_row += f'{{{i}:{fmt_col}}}'
            if frame:
                bar += '-'
                fmt_header += ' '
                fmt_row += ' '
            i += 1

        if frame:
            bar += '+\n'
            fmt_header += '|\n'
            fmt_row += '|\n'
        else:
            bar += '\n'
            fmt_header += '\n'
            fmt_row += '\n'

        return FORMATS(fmt_header, fmt_row, bar)

    def add_rows(self, rows: list[list]):
        """Add multiple rows to the table. The rows should be provided
        as a list with each row itself being a list of columns."""
        for row in rows:
            self.add_row(row)

    def add_row(self, row: list):
        """Add a single row to the table. The row must be provided as a
        list of columns."""
        formatted_row = []
        i = 0
        for value in row:
            fmt_type = self._formats[i][-1]
            if fmt_type == 's':
                formatted_value = str(value)
            elif fmt_type == 'd':
                formatted_value = int(value)
            elif fmt_type == 'f':
                formatted_value = float(value)
            else:
                raise ValueError(f'The format of column {i} (header: ' +
                                 f'{self._headers[i]}) is of an ' +
                                 'unsupported type. ' +
                                 f'format = "{self._formats[i]}"')
            formatted_row.append(formatted_value)
            i += 1

        self._rows.append(formatted_row)
        self._update_column_widths(formatted_row)

    def generate_header(self, frame: bool = False, spacing: int = 3) -> str:
        """Generate the header for the table. Mostly useful if you
        implement your custom generator."""
        formats = self.formats(frame=frame, spacing=spacing)
        if frame:
            output = formats.bar
        else:
            output = ''

        output += formats.header.format(*self._headers)
        output += formats.bar
        return output.rstrip('\n')

    def generate(self, frame: bool = False, spacing: int = 3) -> str:
        """Generate the table and return it as a string.
        The frame argument specifies whether framing should be added to
        the table (MySQL style output) - default is not to add framing.
        """

        if len(self._rows) == 0:
            # No rows, so nothing to generate an output from.
            # Just return an empty string
            return ''

        formats = self.formats(frame=frame, spacing=spacing)
        output = self.generate_header(frame=frame, spacing=spacing)
        output += '\n'
        for row in self._rows:
            output += formats.row.format(*row)
        if frame:
            output += formats.bar

        return output.rstrip('\n')

    def _update_column_widths(self, row: list):
        """Update the column widths by setting it to the maximum of the
        current width and the width of the columns in the provided row.
        """
        i = 0
        for column in row:
            current_width = self._column_widths[i]
            fmt_col = self._fmt_col(i)
            fmt = f'{{0:{fmt_col}}}'
            value_str = fmt.format(column)
            self._column_widths[i] = max(current_width, len(value_str))
            i += 1

    def _ini_column_widths(self):
        """Initialise the maximum column widths with the width of the
        headers."""
        self._column_widths = [len(h) for h in self._headers]

    def _fmt_col(self, column_index: int, width: int or None = None) -> str:
        """Generate the format for a column. The total width of the
        column is optional."""
        if width is None:
            width_str = ''
        else:
            width_str = str(width)
        fmt_specifier = self._formats[column_index]
        header = self._headers[column_index]
        fmt_type = fmt_specifier[-1]
        if fmt_type == 'd':
            fmt_mod = fmt_specifier[0:-1]
            fmt = f'{fmt_mod}{width_str}{fmt_type}'
        elif fmt_type in ('s', 'f'):
            # Strings (can have max width) and floats
            re_format = re.compile(rf'^([^.]+)?(\.\d+)?{fmt_type}$')
            m = re_format.match(self._formats[column_index])
            if m is None:
                raise ValueError(f'The format of column {column_index} (' +
                                 f'header: {header}) is ' +
                                 f'of an unsupported {fmt_type} type. ' +
                                 f'format = "{fmt_specifier}"')
            fmt_mod = m[1] if m[1] is not None else ''
            fmt_precision = m[2] if m[2] is not None else ''
            fmt = f'{fmt_mod}{width_str}{fmt_precision}{fmt_type}'
        else:
            raise ValueError(f'The format of column {column_index} (header: ' +
                             f'{header}) is of an ' +
                             f'unsupported type. Format = "{fmt_specifier}"')

        return fmt
