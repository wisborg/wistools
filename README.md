# wistools
Wistools is a collection of Python tools to make life easier as a developer.

```python
import wistools

table = wistools.Table(['Key', 'Value'], ['s', 'd'])
table.add_row(['Foo', 1], ['Bar', 2])
print(table.generate(framing=True))
```

Generates:

```
+-----+-------+
| Key | Value |
+-----+-------+
| Foo |     1 |
| Bar |     2 |
+-----+-------+
```

## Installing Wistools and Supported Versions

Wistools is installed from GitHub:

```shell
$ python -m pip install https://github.com/wisborg/wistools
```

Wistools have been tested with Python 3.9.

## Supported Features

Wistools supports the following features:

* **Table:** A table generator.

