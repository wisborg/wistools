# wistools
Wistools is a collection of Python tools to make life easier as a developer.

```python
>>> from wistools.table import Table
>>> table = Table(['Key', 'Value'], ['s', 'd'])
>>> table.add_row(['Foo', 1])
>>> table.add_row(['Bar', 2])
>>> print(table.generate(frame=True))
+-----+-------+
| Key | Value |
+-----+-------+
| Foo |     1 |
| Bar |     2 |
+-----+-------+
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
$ python -m pip install git+https://github.com/wisborg/wistools
```

Wistools have been tested with Python 3.9.

## Supported Features

Wistools supports the following features:

* **Table:** A table generator.

