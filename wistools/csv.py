"""
Class for working with CSV files.
"""

from collections import namedtuple
import csv
from pathlib import Path
import re


def _validate_headers(header_row: dict, expected: list):
    actual = [h for h in list(header_row.values())]
    if len(expected) != len(actual):
        raise ValueError(f'The number of headers ({len(actual)} differs ' +
                         f'from the expected ({len(expected)}).')
    for i in range(len(expected)):
        striped = actual[i].strip(' "')
        # For some reason strip() doesn't remove a leading "
        if striped[0] == '"':
            striped = striped[1:]
        if striped != expected[i]:
            err = f'Expected column {i} to have the header ' + \
                  f'"{expected[i]}", but got "{striped}".'
            raise ValueError(err)


def _header_to_property(header: str) -> str:
    """Takes a header and creates a property name for it."""
    # Full list of allowed characters:
    # https://docs.python.org/3/reference/lexical_analysis.html#grammar-token-identifier
    # Here a simplified version is used with [a-zA-Z][a-zA-Z0-9_]* is used.
    # Additionally trailing underscores are removed and the name is converted
    # to lower case.

    # Strip all non-[a-zA-Z] characters from the start of the string
    re1 = re.compile(r'^[^a-zA-Z]+')
    name = re1.sub('', header)
    # Replace all sequences of non-allowed characters with _
    # Include _ itself to avoid ending up with multiple _s in a row.
    re2 = re.compile(r'[^a-zA-Z0-9]+')
    name = re2.sub('_', name)
    # Replace any trailing _
    return name.rstrip('_').lower()


def _headers_to_properties(headers: list) -> list:
    return [_header_to_property(h) for h in headers]


class CsvDict(object):
    _row_name: str = 'CsvRow'
    _row_tuple: namedtuple = None
    _headers: list = []  # The original header names
    _properties: list = []  # The headers converted to valid property names
    _key: str = ''
    _rows: dict = {}

    def __init__(self, row_name: str = 'CsvRow'):
        self._row_name = row_name
        self._row_tuple = namedtuple(row_name, [])
        self._headers = []
        self._properties = []
        self._key = ''
        self._rows = {}

    @property
    def rows(self) -> dict:
        return self._rows

    @property
    def headers(self) -> list:
        return self._headers

    @headers.setter
    def headers(self, headers: list):
        self._headers = headers

    @property
    def properties(self) -> list:
        return self._properties

    @properties.setter
    def properties(self, properties: list):
        self._properties = properties

    @property
    def key(self) -> str:
        return self._key

    @key.setter
    def key(self, key: str):
        if key not in self.properties:
            raise ValueError(f'No header exists with the name "{key}" - ' +
                             f'properties: {self.properties}')
        self._key = key

    def load_file(self, path: (str or Path), key: str = '',
                  headers: (list or tuple) = (),
                  properties: (list or tuple) = (),
                  header_rows: int = 1, validate_headers: bool = False,
                  encoding: str = 'utf-8-sig', delimiter: str = ',',
                  quotechar: str = '"', require_column: str = '',
                  filters: dict = None):
        """Load the content of a CSV file. The path is mandatory.

        The key argument specifies the column header (as a string) that
        should be used as the key in the row dictionary. If no key is
        specified, the first column is used.

        If a list of headers is provided, that will be used as the
        property names instead of the headers read from the file.

        The properties argument can be used to specify the property names.
        If this is given, the number of elements must be the same as the
        number of headers.

        The number of header lines in the file can be specified with
        header_rows. If no headers are provided, the last header line
        is used to determine the headers.

        If validate_headers is true, then the provided list of headers
        must match the headers read from the file.

        The require_column argument can be used to specify the name of
        a column. If that column does not contain a value (the value is
        an empty string), then the row is skipped. This is for example
        useful if there is a row with totals.
        """
        file = Path(path)
        if len(headers) > 0:
            self.headers = headers
        if len(properties) > 0:
            self.properties = properties
        if key != '':
            self.key = key
        with file.open(mode='r', encoding=encoding) as csvfile:
            # Check if the file starts with a byte order mark (BOM)
            csvfile.seek(0)
            i = 0
            if len(self.headers) == 0:
                # Read the headers from the file
                reader = csv.reader(csvfile, delimiter=delimiter,
                                    quotechar=quotechar)
                for row in reader:
                    i += 1
                    if i == header_rows:
                        self.headers = row
                        break

            if len(self.properties) > 0:
                if len(self.properties) != len(self.headers):
                    raise ValueError('The number of properties ' +
                                     f'({len(self.properties)}) does not ' +
                                     'match the number of headers ' +
                                     f'{len(self.headers)}.')
            else:
                self.properties = _headers_to_properties(self.headers)

            if self.key == '':
                # Use the first property as the key
                self.key = self.properties[0]

            self._row_tuple = namedtuple(self._row_name, self.properties)

            csvfile.seek(0)
            i = 0
            reader = csv.DictReader(csvfile, self.headers, delimiter=delimiter,
                                    quotechar=quotechar)
            for row in reader:
                i += 1
                if i == header_rows and validate_headers:
                    # Validate that the read headers are the expected headers
                    # This is trivial if the headers were read from the file
                    _validate_headers(row, self.headers)
                elif i <= header_rows:
                    continue
                else:
                    if require_column != '' and row[require_column] == '':
                        # The row with totals - ignore that
                        continue

                    row_value = self._row_tuple(*row.values())
                    include = True
                    if filters is not None:
                        for key, filter_value in filters.items():
                            value = getattr(row_value, key)
                            if value != filter_value:
                                include = False

                    if include:
                        key_value = getattr(row_value, self.key)
                        self._rows[key_value] = row_value
