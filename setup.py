from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='wistools',
    version='0.0.4',
    author='Jesper Wisborg Krogh',
    author_email='wistools@wisborg.dk',
    description='A collections of Python tools',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/wisborg/wistools',
    project_urls = {
        'Bug Tracker': 'https://github.com/wisborg/wistools/issues'
    },
    license='MIT',
    packages=['wistools'],
    install_requires=[],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
    ],
)
