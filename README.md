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

### Generating Reports

Reports are rendered as html-tables in Jupyter notebooks as shown in the
screenshot above, and otherwise as plain text lists.

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

On top of the default (optional) packages you can provide additional packages,
either as strings or give already imported packages:
```py
>>> import pyvista
>>> import scooby
>>> scooby.Report(additional=[pyvista, 'vtk', 'no_version', 'does_not_exist'])
```
```
--------------------------------------------------------------------------------
  Date: Mon Jul 01 10:55:24 2019 CEST

             Linux : OS
                 4 : CPU(s)
            x86_64 : Machine
             64bit : Architecture
           15.6 GB : RAM
           IPython : Environment

  Python 3.7.3 (default, Mar 27 2019, 22:11:17)  [GCC 7.3.0]

            0.20.4 : pyvista
             8.1.2 : vtk
   Version unknown : no_version
  Could not import : does_not_exist
            1.16.4 : numpy
             1.2.1 : scipy
             7.5.0 : IPython
             3.1.0 : matplotlib
             0.3.0 : scooby

  Intel(R) Math Kernel Library Version 2019.0.4 Product Build 20190411 for
  Intel(R) 64 architecture applications
--------------------------------------------------------------------------------
```
As can be seen, scooby reports if a package could not be imported or if the
version of a package could not be determined.

Other useful parameters are

- `ncol`: number of columns in the html-table;
- `text_width`: text width of the plain-text version;
- `sort`: list is sorted alphabetically if True.

Besides `additional` there are two more lists, `core` and `optional`, which
can be used to provide package names. However, they are mostly useful for
package maintainers wanting to use scooby to create their reporting system.
See below:


### Implementing scooby in your project

You can generate easily your own Report-instance using scooby:

```py
class Report(scooby.Report):
    def __init__(self, additional=None, ncol=3, text_width=80, sort=False):
        """Initiate a scooby.Report instance."""

        # Mandatory packages.
        core = ['yourpackage', 'your_core_packages', 'e.g.', 'numpy', 'scooby']

        # Optional packages.
        optional = ['your_optional_packages', 'e.g.', 'matplotlib']

        super().__init__(additional, core, optional, ncol, text_width, sort)
```

So a user can use your Report:
```py
>>> import your_package
>>> your_package.Report()
```


### Solving Mysteries

Are you struggling with the mystery of whether or not code is being executed in
IPython, Jupyter, or normal Python? Try using some of Scooby's investigative
functions to solve these kinds of mysteries:

```py
import scooby

if scooby.in_ipykernel():
    # Do Jupyter/IPyKernel stuff
elif scooby.in_ipython():
    # Do IPython stuff
else:
    # Do normal, boring Python stuff
```


## Optional Requirements

The following is a list of optional requirements and their purpose:

- `psutil`: report total RAM in GB
- `mkl-services`: report Intel(R) Math Kernel Library version
