from bz2 import BZ2File
from contextlib import contextmanager
from gzip import GzipFile
from mimetypes import guess_type
from pathlib import Path
import re
from zipfile import ZipFile

from unidecode import unidecode

# Regexps for characters not allowed in filename or that should be removed for
# sanity purposes. RE_FILENAME_SPECIAL_2 is substituted with " - ".
# RE_FILENAME_SPECIAL_3 is substituted with "-"
# It is assumed there are no non-printable characters or control characters
# in the information used to generate file names.
RE_FILENAME_SPECIAL_1 = re.compile(r'[<>"\\|?*!]')
RE_FILENAME_SPECIAL_2 = re.compile(r'[:]')
RE_FILENAME_SPECIAL_3 = re.compile(r'[/]')
RE_FILENAME_WS = re.compile(r'\s\s+')


# Source: https://peps.python.org/pep-0343/
@contextmanager
def opened_w_error(filename, mode='r'):
    """Allow opening a file using a "with" statement and still handle
    exceptions occurring while opening the file. Example usage:

    with opened_w_error('/etc/passwd', 'a') as (f, err):
        if err:
            print(f'IOError: {err}')
        else:
            f.write('guido::0:0::/:/bin/sh\n')
    """
    try:
        f = open(filename, mode)
    except IOError as err:
        yield None, err
    else:
        try:
            yield f, None
        finally:
            f.close()


def open_file(filepath: (str or Path), mode: str = 'rb',
              encoding: (str or None) = None, compresslevel: int = 9):
    """Open a file with optionally transparent compression.
    Supported compression types are: None (plain text or binary), gzip,
    bzip2, and zip. Unknown encodings are treated as None.

    If encoding=None (the default) and the file already exists, the
    encoding will be the same as for the existing file.

    If the filepath is a link, the real path is found and a socket to
    the target file is opened.
    """

    file = Path(filepath).resolve()
    if encoding is None and file.is_file():
        # Determine the file type.
        (mimetype, encoding) = guess_type(file, False)

        if encoding is None:
            if mimetype in ('application/zip',
                            'application/vnd.google-earth.kmz',
                            'application/epub+zip'):
                encoding = 'zip'
        if encoding not in (None, 'gzip', 'bzip2', 'zip'):
            # Text (None), gzip, and bzip2 currently supported.
            # The encoding found is not one of those, so treat as None.
            encoding = None

    if encoding == 'gzip':
        fs = GzipFile(filename=file, mode=mode, compresslevel=compresslevel)
    elif encoding == 'bzip2':
        fs = BZ2File(file, mode=mode, compresslevel=compresslevel)
    elif encoding == 'zip':
        fs = ZipFile(file, mode=mode, compresslevel=compresslevel)
    else:
        fs = file.open(mode=mode, encoding=encoding)

    return fs


def sanitize_filename(filename: str) -> str:
    """Takes a filename (without path) and replaces accented
    characters with their unaccented equivalent and attempts to
    remove characters not supported on common file systems."""
    # Replace all accented characters with their unaccented equivalent
    no_accents = unidecode(filename)

    # Also try to remove characters that are known to be forbidden on Windows
    # or Linux.
    no_special1 = RE_FILENAME_SPECIAL_1.sub('', no_accents)
    no_special2 = RE_FILENAME_SPECIAL_2.sub(' - ', no_special1)
    no_special3 = RE_FILENAME_SPECIAL_3.sub('-', no_special2)

    # Change consecutive whitespace characters to single space
    return RE_FILENAME_WS.sub(' ', no_special3)


def get_files(locations: list[Path] or list[str], glob: str) -> list[Path]:
    files = []
    for location in locations:
        path = Path(location.rstrip('\\'))
        if path.is_dir():
            candidates = path.glob(glob)
            for candidate in candidates:
                if candidate.is_file():
                    files.append(candidate)
        elif path.is_file():
            files.append(path)

    return files
