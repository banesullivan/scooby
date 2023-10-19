# 🐶🕵️ Scooby

[![Tests](https://github.com/banesullivan/scooby/actions/workflows/pythonpackage.yml/badge.svg)](https://github.com/banesullivan/scooby/actions/workflows/pythonpackage.yml)
[![PyPI Status](https://img.shields.io/pypi/v/scooby.svg?logo=python&logoColor=white)](https://pypi.org/project/scooby/)
[![Conda Status](https://img.shields.io/conda/vn/conda-forge/scooby.svg)](https://anaconda.org/conda-forge/scooby)
[![codecov](https://codecov.io/gh/banesullivan/scooby/branch/main/graph/badge.svg?token=eJqZ700tqH)](https://codecov.io/gh/banesullivan/scooby)

*Great Dane turned Python environment detective*

This is a lightweight tool for easily reporting your Python environment's
package versions and hardware resources.


Install from [PyPI](https://pypi.org/project/scooby/)

```bash
pip install scooby
```

or from [conda-forge](https://anaconda.org/conda-forge/scooby/)

```bash
conda install -c conda-forge scooby
```

![Jupyter Notebook Formatting](https://github.com/banesullivan/scooby/raw/main/assets/jupyter.png)

Scooby has HTML formatting for Jupyter notebooks and rich text formatting for
just about every other environment. We designed this module to be lightweight
such that it could easily be added as a dependency to Python projects for
environment reporting when debugging. Simply add scooby to your dependencies
and implement a function to have scooby report on the aspects of the
environment you care most about.

If scooby is unable to detect aspects of an environment that you'd like to
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
screenshot above, and otherwise as plain text lists. If you do not output the
`Report` object either at the end of a notebook cell or it is generated
somewhere in a vanilla Python script, you may have to print the `Report`
object: `print(scooby.Report())`, but note that this will only output the plain
text representation of the script.

```py
>>> import scooby
>>> scooby.Report()
```
```
--------------------------------------------------------------------------------
  Date: Wed Feb 12 15:35:43 2020 W. Europe Standard Time

                OS : Windows
            CPU(s) : 16
           Machine : AMD64
      Architecture : 64bit
               RAM : 31.9 GiB
       Environment : IPython

  Python 3.7.6 | packaged by conda-forge | (default, Jan  7 2020, 21:48:41)
  [MSC v.1916 64 bit (AMD64)]

             numpy : 1.18.1
             scipy : 1.3.1
           IPython : 7.12.0
        matplotlib : 3.0.3
            scooby : 0.5.0

  Intel(R) Math Kernel Library Version 2019.0.4 Product Build 20190411 for
  Intel(R) 64 architecture applications
--------------------------------------------------------------------------------
```

For all the Scooby-Doo fans out there, `doo` is an alias for `Report` so you
can oh-so satisfyingly do:

```py
>>> import scooby
>>> scooby.doo()
```
```
--------------------------------------------------------------------------------
  Date: Thu Nov 25 09:47:50 2021 MST

                OS : Darwin
            CPU(s) : 12
           Machine : x86_64
      Architecture : 64bit
               RAM : 32.0 GiB
       Environment : Python
       File system : apfs

  Python 3.8.12 | packaged by conda-forge | (default, Oct 12 2021, 21:50:38)
  [Clang 11.1.0 ]

             numpy : 1.21.4
             scipy : 1.7.3
           IPython : 7.29.0
        matplotlib : 3.5.0
            scooby : 0.5.8
--------------------------------------------------------------------------------
```

Or better yet:

```py
from scooby import doo as doobiedoo
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
  Date: Wed Feb 12 16:15:15 2020 W. Europe Standard Time

                OS : Windows
            CPU(s) : 16
           Machine : AMD64
      Architecture : 64bit
               RAM : 31.9 GiB
       Environment : IPython

  Python 3.7.6 | packaged by conda-forge | (default, Jan  7 2020, 21:48:41)
  [MSC v.1916 64 bit (AMD64)]

           pyvista : 0.23.1
               vtk : 8.1.2
        no_version : Version unknown
    does_not_exist : Could not import
             numpy : 1.18.1
             scipy : 1.3.1
           IPython : 7.12.0
        matplotlib : 3.0.3
            scooby : 0.5.0

  Intel(R) Math Kernel Library Version 2019.0.4 Product Build 20190411 for
  Intel(R) 64 architecture applications
--------------------------------------------------------------------------------
```

Furthermore, scooby reports if a package could not be imported or if the
version of a package could not be determined.

Other useful parameters are

- `ncol`: number of columns in the html-table;
- `text_width`: text width of the plain-text version;
- `sort`: list is sorted alphabetically if True.

Besides `additional` there are two more lists, `core` and `optional`, which
can be used to provide package names. However, they are mostly useful for
package maintainers wanting to use scooby to create their reporting system
(see below).


### Implementing scooby in your project

You can easily generate a custom `Report` instance using scooby within your
project:

```py
class Report(scooby.Report):
    def __init__(self, additional=None, ncol=3, text_width=80, sort=False):
        """Initiate a scooby.Report instance."""

        # Mandatory packages.
        core = ['yourpackage', 'your_core_packages', 'e.g.', 'numpy', 'scooby']

        # Optional packages.
        optional = ['your_optional_packages', 'e.g.', 'matplotlib']

        scooby.Report.__init__(self, additional=additional, core=core,
                               optional=optional, ncol=ncol,
                               text_width=text_width, sort=sort)
```

This makes it particularly easy for a user of your project to quickly generate
a report on all of the relevant package versions and environment details when
sumbitting a bug.

```py
>>> import your_package
>>> your_package.Report()
```

The packages on the `core`-list are the mandatory ones for your project, while
the `optional`-list can be used for optional packages. Keep the
`additional`-list free to allow your users to add packages to the list.

#### Implementing as a soft dependency

If you would like to implement scooby, but are hesitant to add another
dependency to your package, here is an easy way how you can use scooby as a
soft dependency. Instead of `import scooby` use the following snippet:

```py
# Make scooby a soft dependency:
try:
    from scooby import Report as ScoobyReport
except ImportError:
    class ScoobyReport:
        def __init__(self, *args, **kwargs):
            message = (
                '\n  *ERROR*: `Report` requires `scooby`.'
                '\n           Install it via `pip install scooby` or'
                '\n           `conda install -c conda-forge scooby`.\n'
            )
            raise ImportError(message)
```

and then create your own `Report` class same as above,

```py
class Report(ScoobyReport):
    def __init__(self, additional=None, ncol=3, text_width=80, sort=False):
        """Initiate a scooby.Report instance."""

        # Mandatory packages.
        core = ['yourpackage', 'your_core_packages', 'e.g.', 'numpy', 'scooby']

        # Optional packages.
        optional = ['your_optional_packages', 'e.g.', 'matplotlib']

        scooby.Report.__init__(self, additional=additional, core=core,
                               optional=optional, ncol=ncol,
                               text_width=text_width, sort=sort)

```
If a user has scooby installed, all works as expected. If scooby is not
installed, it will raise the following exception:

```py
>>> import your_package
>>> your_package.Report()

  *ERROR*: `Report` requires `scooby`
           Install it via `pip install scooby` or
           `conda install -c conda-forge scooby`.
```

### Solving Mysteries

Are you struggling with the mystery of whether or not code is being executed in
IPython, Jupyter, or normal Python? Try using some of scooby's investigative
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

### How does scooby get version numbers?

A couple of locations are checked, and we are happy to implement more if
needed, just open an issue!

Currently, it looks in the following places:
- `__version__`
- `version`
- lookup `VERSION_ATTRIBUTES` in the scooby knowledge base
- lookup `VERSION_METHODS` in the scooby knowledge base

`VERSION_ATTRIBUTES` is a dictionary of attributes for known python packages
with a non-standard place for the version. You can add other known places via:

```py
scooby.knowledge.VERSION_ATTRIBUTES['a_module'] = 'Awesome_version_location'
```

Similarly, `VERSION_METHODS` is a dictionary for methods to retrieve the
version, and you can similarly add your methods which will get the version
of a package.

### Using scooby to get version information.

If you are only interested in the version of a single package then you can use
scooby as well. A few examples:

```py
>>> import scooby, numpy
>>> scooby.get_version(numpy)
('numpy', '1.16.4')
>>> scooby.get_version('no_version')
('no_version', 'Version unknown')
>>> scooby.get_version('does_not_exist')
('does_not_exist', 'Could not import')
```

Note that modules can be provided as already loaded ones or as strings.


### Tracking Imports in a Session

Scooby has the ability to track all imported modules during a Python session
such that *any* imported, non-standard lib package that is used in the session
is reported by a `TrackedReport`. For instance, start a session by importing
scooby and enabling tracking with the `track_imports()` function.
Then *all* subsequent packages that are imported during the session will be
tracked and scooby can report their versions.
Once you are ready to generate a `Report`, instantiate a `TrackedReport` object.

In the following example, we import a constant from `scipy` which will report
the versions of `scipy` and `numpy` as both packages are loaded in the session
(note that `numpy` is internally loaded by `scipy`).

```py
>>> import scooby
>>> scooby.track_imports()

>>> from scipy.constants import mu_0 # a float value

>>> scooby.TrackedReport()
```
```
--------------------------------------------------------------------------------
  Date: Thu Apr 16 15:33:11 2020 MDT

                OS : Linux
            CPU(s) : 8
           Machine : x86_64
      Architecture : 64bit
               RAM : 62.7 GiB
       Environment : IPython

  Python 3.7.7 (default, Mar 10 2020, 15:16:38)  [GCC 7.5.0]

            scooby : 0.5.2
             numpy : 1.18.1
             scipy : 1.4.1
--------------------------------------------------------------------------------
```

## Command-Line Interface

Scooby comes with a command-line interface. Simply typing

```bash
scooby
```

in a terminal will display the default report. You can also use it to show the
scooby-report of another package, if that package has scooby implemented as
suggested above, using `packagename.Report()`. As an example, to print the
report of pyvista you can run

```bash
scooby --report pyvista
```

which will show the report of PyVista.

Simply type

```bash
scooby --help
```

to see all the possibilities.


## Optional Requirements

The following is a list of optional requirements and their purpose:

- `psutil`: report total RAM in GiB
- `mkl-services`: report Intel(R) Math Kernel Library version
