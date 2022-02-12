import re

RE_VALIDATE_ID = re.compile(r'^[1-9]\d*$')
RE_VALIDATE_FLOAT = re.compile(r'^(?:\d+|(?:\d+)?\.(?:\d+)?)$')


def ask(prompt: str, answer_type: str, default=None, allow_none: bool = True,
        multiline: bool = False):
    if default is not None:
        question = '{0} [{1}]'.format(prompt, str(default))
    else:
        question = '{0}'.format(prompt)

    if answer_type == 'bool':
        question += ' (Y/N/YES/NO): '
    elif multiline:
        question += ' (empty line or EOF to stop)'
    else:
        question += ': '

    keep_asking = True
    answer = None
    paragraphs = []
    while keep_asking:
        if multiline:
            try:
                answer = input().strip()
            except EOFError:
                answer = ''
            if answer:
                paragraphs.append(answer)
                print('\n')
            else:
                answer = '\n\n'.join(paragraphs)
        else:
            answer = input(question)
        if answer == '':
            answer = str(default) if default is not None else None

        valid, answer = validate(answer, answer_type, allow_none)
        if valid:
            keep_asking = False
        else:
            print('Invalid answer. Expected type: {0}'.format(answer_type))

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
