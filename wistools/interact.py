from platform import system
import re

# On macOS the maximum size of the buffer is limited to 1KiB. A workaround
# is to import readline. The readline module is not explicitly used anywhere.
# https://stackoverflow.com/questions/7357007/python-raw-input-limit-with-mac-os-x-terminal
if system() == 'Darwin':
    import readline

RE_VALIDATE_ID = re.compile(r'^[1-9]\d*$')
RE_VALIDATE_FLOAT = re.compile(r'^(?:\d+|(?:\d+)?\.(?:\d+)?)$')
RE_VALIDATE_INT = re.compile(r'^-?\d+$')


def _ask_normal(question: str, answer_type: str, default, allow_none: bool):
    """Internal routine for asking for a single line answer."""
    keep_asking = True
    answer = None
    while keep_asking:
        answer = input(question)
        if answer == '':
            answer = str(default) if default is not None else None

        valid, answer = validate(answer, answer_type, allow_none)
        if valid:
            keep_asking = False
        else:
            print(f'Invalid answer. Expected type: {answer_type}')

    return answer


def _ask_multiline(question: str, default, allow_none: bool):
    """Internal routine to ask for a multiline answer."""
    re_colon = re.compile(r'^(.+):\s*$')
    m = re_colon.match(question)
    if system() == 'Windows':
        eof = 'CTRL+Z + Enter'
    else:
        eof = 'CTRL-D'
    eof_instructions = f'(empty line or EOF - {eof} - to stop)'
    if m is None:
        print(f'{question} {eof_instructions}:')
    else:
        print(f'{m[1]} {eof_instructions}:')

    keep_asking = True
    answer = None
    lines = []
    while keep_asking:
        try:
            line = input()
        except EOFError:
            answer = '\n'.join(lines)

            if answer == '':
                answer = str(default) if default is not None else None

            valid, answer = validate(answer, 'string', allow_none)
            if valid:
                keep_asking = False
            else:
                print('Invalid answer. Expected type: string')
                lines = []
        else:
            lines.append(line)
            print('')

    return answer


def ask(prompt: str, answer_type: str, default=None, allow_none: bool = True,
        multiline: bool = False):
    """Interactively ask the user for an answer to a question. Supported
    answer types are the same as those supported by validate(). If
    allow_none is True, then an empty answer is allowed and returned as
    None. If multiline is True, the answer can consist of multiple
    lines."""
    if default is not None:
        question = f'{prompt} [{default}]'
    else:
        question = prompt

    if answer_type == 'bool':
        question += ' (Y/N/YES/NO): '
    else:
        question += ': '

    if multiline:
        answer = _ask_multiline(question, default, allow_none)
    else:
        answer = _ask_normal(question, answer_type, default, allow_none)

    return answer


def validate(value, valid_type, allow_none=True):
    """Validate a value based on the expected type. Supported types are:
    id (positive integer), float, bool, and string."""
    valid = False
    validated_value = None
    if value is None:
        valid = allow_none
    else:
        if valid_type == 'id':
            if RE_VALIDATE_ID.match(value):
                valid = True
                validated_value = int(value)
        elif valid_type == 'integer':
            print(f'value ..........: "{value}"')
            if RE_VALIDATE_INT.match(value):
                valid = True
                validated_value = int(value)
        elif valid_type == 'bool':
            valid = value.upper() in ('Y', 'YES', 'N', 'NO')
            if valid:
                validated_value = value.upper() in ('Y', 'YES')
        elif valid_type == 'float':
            if RE_VALIDATE_FLOAT.match(value):
                valid = True
                validated_value = float(value)
        elif valid_type == 'string':
            valid = True
            validated_value = str(value)

    return valid, validated_value
