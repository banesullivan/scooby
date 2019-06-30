# Scooby

[![Build Status](https://travis-ci.org/banesullivan/scooby.svg?branch=master)](https://travis-ci.org/banesullivan/scooby)
[![PyPI Status](https://img.shields.io/pypi/v/scooby.svg?logo=python&logoColor=white)](https://pypi.org/project/scooby/)


A Great Dane turned Python environment detective

This is a lightweight toolset to easily report your Python environment's
package versions and hardware resources.


Install from [PyPI](https://pypi.org/project/scooby/):

```bash
pip install scooby
```

![Jupyter Notebook Formatting](https://github.com/banesullivan/scooby/raw/master/assets/jupyter.png)

Scooby has HTML formatting for Jupyter notebooks and rich text formatting for
just about every other environment. We designed this module to be lightweight
such that it could easily be added as a dependency to Python projects for
environment reporting when debugging. Simply add `scooby` to your dependencies
and implement a function to have `scooby` report on the aspects of the
environment you care most about.

If `scooby` is unable to detect aspects of an environment that you'd like to
know, please share this with us as a feature requests or pull requests.






The scooby reporting is derived from the versioning-scripts created by [Dieter
Werthmüller](https://github.com/prisae) for
[empymod](https://empymod.github.io), [emg3d](https://empymod.github.io), and
the [SimPEG](https://github.com/simpeg/) framework. It was heavily inspired by
`ipynbtools.py` from [qutip](https://github.com/qutip) and
[`watermark.py`](https://github.com/rasbt/watermark). This package has been
altered to create a lightweight implementation so that it can easily be used as
an environment reporting tool in any Python library with minimal impact.

## Usage

### Solving Mysteries

Are you struggling with the mystery of whether or not code is being executed in
IPython, Jupyter, or normal Python? Try using some of Scooby's investigative
functions to solve these kinds of mysteries:

```py
import scooby

if scooby.in_ipykernel():
    # Do Jupyter stuff
elif scooby.in_ipython():
    # Do IPython stuff
else:
    # Do normal, boring Python stuff
```

### Generating Reports

Use Scooby's `Report` objects. These objects have representation methods
implemented so that if outputted, they show a nicely formatted report but you
could also capture the report as an object itself.

```py
>>> import scooby
>>> scooby.Report()
```
```
--------------------------------------------------------------------------------
  Date: Sun Jun 30 12:51:42 2019 MDT

            Darwin : OS
                12 : CPU(s)
            x86_64 : Machine
             64bit : Architecture
           32.0 GB : RAM
            Python : Environment

  Python 3.7.3 | packaged by conda-forge | (default, Mar 27 2019, 15:43:19)
  [Clang 4.0.1 (tags/RELEASE_401/final)]

            1.16.3 : numpy
             1.3.0 : scipy
             7.5.0 : IPython
             3.1.0 : matplotlib
             0.2.2 : scooby

  Intel(R) Math Kernel Library Version 2018.0.3 Product Build 20180406 for
  Intel(R) 64 architecture applications
--------------------------------------------------------------------------------
```

But you can also add addtional packages too if you'd like via the `addtional`
keyword argument:

```py
>>> scooby.Report(additional='pyvista')
```
```
--------------------------------------------------------------------------------
  Date: Sun Jun 30 12:52:14 2019 MDT

            Darwin : OS
                12 : CPU(s)
            x86_64 : Machine
             64bit : Architecture
           32.0 GB : RAM
            Python : Environment

  Python 3.7.3 | packaged by conda-forge | (default, Mar 27 2019, 15:43:19)
  [Clang 4.0.1 (tags/RELEASE_401/final)]

            0.20.4 : pyvista
            1.16.3 : numpy
             1.3.0 : scipy
             7.5.0 : IPython
             3.1.0 : matplotlib
             0.2.2 : scooby

  Intel(R) Math Kernel Library Version 2018.0.3 Product Build 20180406 for
  Intel(R) 64 architecture applications
--------------------------------------------------------------------------------
```

Or maybe you want a whole bunch of additional packages:

```py
>>> scooby.Report(additional=['pyvista', 'vtk', 'appdirs',])
```
```
--------------------------------------------------------------------------------
  Date: Sun Jun 30 12:52:37 2019 MDT

            Darwin : OS
                12 : CPU(s)
            x86_64 : Machine
             64bit : Architecture
           32.0 GB : RAM
            Python : Environment

  Python 3.7.3 | packaged by conda-forge | (default, Mar 27 2019, 15:43:19)
  [Clang 4.0.1 (tags/RELEASE_401/final)]

            0.20.4 : pyvista
             8.2.0 : vtk
             1.4.3 : appdirs
            1.16.3 : numpy
             1.3.0 : scipy
             7.5.0 : IPython
             3.1.0 : matplotlib
             0.2.2 : scooby

  Intel(R) Math Kernel Library Version 2018.0.3 Product Build 20180406 for
  Intel(R) 64 architecture applications
--------------------------------------------------------------------------------
```


Want to add a package to investigate but aren't sure if it is present, simply
define the `optional` list in the arguments. Note that the default libraries of
`numpy`, `scipy`, `IPython`, and `matplotlib` (and `scooby`) are defaults for
optional argument, so you might want to put those in the `core` argument if you
care about those.

```py
>>> scooby.Report(core=['numpy', 'matplotlib'], optional=['foo', ])
```
```
--------------------------------------------------------------------------------
  Date: Sun Jun 30 12:52:58 2019 MDT

            Darwin : OS
                12 : CPU(s)
            x86_64 : Machine
             64bit : Architecture
           32.0 GB : RAM
            Python : Environment

  Python 3.7.3 | packaged by conda-forge | (default, Mar 27 2019, 15:43:19)
  [Clang 4.0.1 (tags/RELEASE_401/final)]

            1.16.3 : numpy
             3.1.0 : matplotlib

  Intel(R) Math Kernel Library Version 2018.0.3 Product Build 20180406 for
  Intel(R) 64 architecture applications
--------------------------------------------------------------------------------
```

Since the `foo` package wasn't found and it's optional, nothing is reported.
But what if you need some sort of error message that a package wasn't found?
Then add your package to the `additional` list and Scooby will report it, just
with a `NA`:

```py
>>> scooby.Report(additional=['foo',])
```
```
--------------------------------------------------------------------------------
  Date: Sun Jun 30 12:53:20 2019 MDT

            Darwin : OS
                12 : CPU(s)
            x86_64 : Machine
             64bit : Architecture
           32.0 GB : RAM
            Python : Environment

  Python 3.7.3 | packaged by conda-forge | (default, Mar 27 2019, 15:43:19)
  [Clang 4.0.1 (tags/RELEASE_401/final)]

  Could not import : foo
            1.16.3 : numpy
             1.3.0 : scipy
             7.5.0 : IPython
             3.1.0 : matplotlib
             0.2.2 : scooby

  Intel(R) Math Kernel Library Version 2018.0.3 Product Build 20180406 for
  Intel(R) 64 architecture applications
--------------------------------------------------------------------------------
```


And you can also sort the packages alphabetically with the `sort` argument:

```py
>>> scooby.Report(additional=['pyvista', 'vtk', 'appdirs',], sort=True)
```
```
--------------------------------------------------------------------------------
  Date: Sun Jun 30 12:54:31 2019 MDT

            Darwin : OS
                12 : CPU(s)
            x86_64 : Machine
             64bit : Architecture
           32.0 GB : RAM
            Python : Environment

  Python 3.7.3 | packaged by conda-forge | (default, Mar 27 2019, 15:43:19)
  [Clang 4.0.1 (tags/RELEASE_401/final)]

             1.4.3 : appdirs
             7.5.0 : IPython
             3.1.0 : matplotlib
            1.16.3 : numpy
            0.20.4 : pyvista
             1.3.0 : scipy
             0.2.2 : scooby
             8.2.0 : vtk

  Intel(R) Math Kernel Library Version 2018.0.3 Product Build 20180406 for
  Intel(R) 64 architecture applications
--------------------------------------------------------------------------------
```


## Optional Requirements

The following is a list of optional requirements and their purpose:

- `psutil`: report total RAM in GB
- `mkl`: report Intel(R) Math Kernel Library version
