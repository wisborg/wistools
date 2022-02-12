import re

RE_VALIDATE_ID = re.compile(r'^[1-9]\d*$')
RE_VALIDATE_FLOAT = re.compile(r'^(?:\d+|(?:\d+)?\.(?:\d+)?)$')


def _ask_normal(question: str, answer_type: str, default, allow_none: bool):
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
    keep_asking = True
    answer = None
    paragraphs = []
    print(question)
    while keep_asking:
        try:
            paragraph = input().rstrip()
        except EOFError:
            paragraph = ''

        if paragraph:
            paragraphs.append(paragraph)
            print('')
        else:
            answer = '\n\n'.join(paragraphs)

            if answer == '':
                answer = str(default) if default is not None else None

            valid, answer = validate(answer, 'string', allow_none)
            if valid:
                keep_asking = False
            else:
                print('Invalid answer. Expected type: string')
                paragraphs = []

    return answer


def ask(prompt: str, answer_type: str, default=None, allow_none: bool = True,
        multiline: bool = False):
    if default is not None:
        question = f'{prompt} [{default}]'
    else:
        question = prompt

    if answer_type == 'bool':
        question += ' (Y/N/YES/NO): '
    elif multiline:
        question += ' (empty line or EOF to stop)'
    else:
        question += ': '

    if multiline:
        answer = _ask_multiline(question, default, allow_none)
    else:
        answer = _ask_normal(question, answer_type, default, allow_none)

    return answer


def validate(value, valid_type, allow_none=True):
    valid = False
    validated_value = None
    if value is None:
        valid = allow_none
    else:
        if valid_type == 'id':
            if RE_VALIDATE_ID.match(value):
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
