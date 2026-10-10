# Installation

## Introduction

This guide shows a couple of ways to install the project in a virtual environment.

## project files

Install the project files by cloning the GitHub repository. If you intend to contribute to the project, or run your own instance, you will likely want to clone your own fork

```
git clone https://github.com/<your_git_hub_id>/pysystemtrade.git
```

otherwise, you'll want the main repo

```
git clone https://github.com/pst-group/pysystemtrade.git
```


## Option 1: pyenv + venv 

### pyenv

pyenv is a tool that makes it easy to manage multiple versions of Python on the same machine. It allows the version of Python used to be defined at the user and project level. It is a great tool, easy to use, and does its one job very well. It is worth reading the introduction to have an overview of how it works at a high level. It's not necessary to understand the technical internals 

https://github.com/pyenv/pyenv#how-it-works

Installation instructions for pyenv are here:

https://github.com/pyenv/pyenv#installation


First install Python itself. pysystemtrade currently requires Python 3.11 or newer. We'll use 3.12

```
$ pyenv install 3.12
```

Once complete you should be able to see the new version in the output of `pyenv versions`

```
$ pyenv versions
  system
  3.9.6
  3.9.13
  3.11.4
  3.11.10
  3.12.4
* 3.12.5
```

Your output will be different, it's just an example

### venv

https://docs.python.org/3.12/library/venv.html

Now we want to create a virtual environment (venv) for the project. Doing this will keep all the dependencies for pysystemtrade separate from your other Python projects

```
$ cd pysystemtrade
$ python -m venv .venv
```

This will create a brand new, isolated Python environment *inside the pysystemtrade project* at the directory
`<your_path>/pysystemtrade/.venv`. You can give your environment any name (the *.venv* bit).

Now activate the virtual environment

```
source .venv/bin/activate
```

Once your virtual env is activated, the prompt will change. It will look something like 

```
(.venv) $
```
This reminds you that your venv is active. You can exit the venv at any time by running `deactivate`

Now we will want to let pyenv know that we want to use Python 3.12 for this project

```
pyenv local 3.12
```

this creates a file at the top level of the project `.python-version` that lets the Python execution environment know to use version 3.12. We can check this by running `python`

```
$ python
Python 3.12.12 (main, Jan 13 2026, 17:48:58) [Clang 21.1.4 ]
Type "help", "copyright", "credits" or "license" for more information.
>>> 
< ctrl-D to exit >
```

### dependencies

Now it's time to start setting up the venv. First update the basic tools

```
(.venv) $ pip install --upgrade pip setuptools
```

And now install the project and its dependencies

```
(.venv) $ python -m pip install '.[parquet]'
```

> We need to specify the `parquet` optional dependency because this project still supports storing time series data in an older format. See [here](/docs/backtesting.md#backtesting-with-arctic-instead-of-parquet) for more details

Or, if you intend to contribute to the project, you will need the optional development dependencies too, and will want to install in *editable* mode

```
(.venv) $ python -m pip install --editable '.[parquet,dev]'
```

Check what is installed, should look something like

```
(.venv) % pip list
Package           Version
----------------- ----------- 
aeventkit         2.1.0
contourpy         1.4.0
cycler            0.12.1
dnspython         2.8.0
fonttools         4.66.1
formulaic         1.2.2
ib-async          2.1.0
interface-meta    2.0.1
kiwisolver        1.5.1
matplotlib        3.11.2
narwhals          2.26.0
nest-asyncio      1.6.0
numpy             2.5.3
packaging         26.3
pandas            2.3.3
patsy             1.0.3
pillow            12.3.0
psutil            7.2.2
pyarrow           25.0.1
pymongo           4.18.2
pyparsing         3.3.3
pypdf2            3.0.1
pysystemtrade     1.8.3
python-dateutil   2.9.0.post0
pytz              2026.4
pyyaml            6.0.3
scipy             1.18.1
six               1.17.0
statsmodels       0.15.0
typing-extensions 4.16.0
tzdata            2025.3
wrapt             2.5.0
```

## Option 2: uv

[uv](https://github.com/astral-sh/uv) is packaging tool that combines the functionality of pip, pyenv, venv and more; read about it [here](https://docs.astral.sh/uv/). It is written in Rust and **extremely** fast

Installation instructions for uv are here:

https://docs.astral.sh/uv/getting-started/installation/


First install Python itself. Pysystemtrade currently requires Python 3.11 or newer; we'll use 3.12

```
$ uv python install 3.12
```

Once complete you should be able to see the new version in the output of `uv python list`

```

cpython-3.14.6-macos-aarch64-none                    /Users/xxx/.local/share/uv/python/cpython-3.14-macos-aarch64-none/bin/python3.14
cpython-3.14.3-macos-aarch64-none                    /opt/homebrew/bin/python3.14 -> ../Cellar/python@3.14/3.14.3_1/bin/python3.14
cpython-3.14.3-macos-aarch64-none                    /opt/homebrew/bin/python3 -> ../Cellar/python@3.14/3.14.3_1/bin/python3
cpython-3.13.15-macos-aarch64-none                   <download available>
cpython-3.13.12-macos-aarch64-none                   /opt/homebrew/bin/python3.13 -> ../Cellar/python@3.13/3.13.12_1/bin/python3.13
cpython-3.13.11-macos-aarch64-none                   /Users/xxx/.local/share/uv/python/cpython-3.13-macos-aarch64-none/bin/python3.13
cpython-3.12.14-macos-aarch64-none                   <download available>
cpython-3.12.12-macos-aarch64-none                   /Users/xxx/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12
cpython-3.12.4-macos-aarch64-none                    /Users/xxx/miniconda3/bin/python3.12
cpython-3.12.4-macos-aarch64-none                    /Users/xxx/miniconda3/bin/python -> python3.12
cpython-3.11.16-macos-aarch64-none                   <download available>
cpython-3.11.11-macos-aarch64-none                   /Users/xxx/.local/share/uv/python/cpython-3.11-macos-aarch64-none/bin/python3.11
cpython-3.10.21-macos-aarch64-none                   <download available>
cpython-3.10.16-macos-aarch64-none                   /Users/xxx/.local/share/uv/python/cpython-3.10-macos-aarch64-none/bin/python3.10
cpython-3.10.13-macos-aarch64-none                   /Users/xxx/.local/share/uv/python/cpython-3.10.13-macos-aarch64-none/bin/python3.10
pypy-3.12.14-macos-aarch64-none                      <download available>
pypy-3.11.16-macos-aarch64-none                      <download available>
pypy-3.10.16-macos-aarch64-none                      <download available>
pypy-3.9.19-macos-aarch64-none                       <download available>
pypy-3.8.16-macos-aarch64-none                       <download available>
```

We pin the version of Python we will use for this project

```
$ uv python pin 3.12
```

and now we want to create a virtual environment for the project with Python 3.12

```
$ uv venv --python 3.12
```

This will create a brand new, isolated Python environment *inside the pysystemtrade project* at the directory
`<your_path>/pysystemtrade/.venv`.

You will see
```
Using CPython 3.12.12
Creating virtual environment at: 3.12
Activate with: source .venv/bin/activate
```

Now activate the virtual environment as instructed.
```
source .venv/bin/activate
```

Once your virtual env is activated, the prompt will change. It will look something like

```
(pysystemtrade) $
```
This reminds you that your virtual environment is active. You can exit the virtual environment at any time by running `deactivate`

We can check this by running `python`

```
$ python
Python 3.12.12 (main, Jan 13 2026, 17:48:58) [Clang 21.1.4 ]
Type "help", "copyright", "credits" or "license" for more information.
>>>
< ctrl-D to exit >
```

### dependencies

And now install the project and its dependencies

```
(pysystemtrade) $ uv pip install '.[parquet]'
```

> We need to specify the `parquet` optional dependency because this project still supports storing time series data in an older format. See [here](/docs/backtesting.md#backtesting-with-arctic-instead-of-parquet) for more details

Or, if you intend to contribute to the project, you will need the optional development dependencies too, and will want to install in *editable* mode

```
(pysystemtrade) $ uv pip install --editable '.[parquet,dev]'
```

Check what is installed, should look something like

```
(pysystemtrade) $ uv pip list
Package           Version     Editable project location
----------------- ----------- ---------------------------------
aeventkit         2.1.0
contourpy         1.4.0
cycler            0.12.1
dnspython         2.8.0
fonttools         4.66.1
formulaic         1.2.2
ib-async          2.1.0
interface-meta    2.0.1
kiwisolver        1.5.1
matplotlib        3.11.2
narwhals          2.26.0
nest-asyncio      1.6.0
numpy             2.5.3
packaging         26.3
pandas            2.3.3
patsy             1.0.3
pillow            12.3.0
psutil            7.2.2
pyarrow           25.0.1
pymongo           4.18.2
pyparsing         3.3.3
pypdf2            3.0.1
pysystemtrade     1.8.3       /home/user/pysystemtrade
python-dateutil   2.9.0.post0
pytz              2026.4
pyyaml            6.0.3
scipy             1.18.1
six               1.17.0
statsmodels       0.15.0
typing-extensions 4.16.0
tzdata            2025.3
wrapt             2.5.0
```


## test

Check stuff works

```
(.venv) $ python
>>>
>>> from sysdata.sim.csv_futures_sim_data import csvFuturesSimData
Configuring sim logging
>>> data=csvFuturesSimData()
>>> data
csvFuturesSimData object with 249 instruments
>>>
```
