# Scooby

[![Build Status](https://travis-ci.org/banesullivan/scooby.svg?branch=master)](https://travis-ci.org/banesullivan/scooby)
[![PyPI Status](https://img.shields.io/pypi/v/scooby.svg?logo=python&logoColor=white)](https://pypi.org/project/scooby/)


A Great Dane turned Python environment detective

This is a toolset to easily report your Python environment's package versions
and hardware resources.

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

This work is derived from [Dieter Werthmüller](https://github.com/prisae)'s work
towards creating a version reporting tool for the [empymod](https://github.com/empymod/)
and [SimPEG](https://github.com/simpeg/) projects.
This package has been altered to create a lightweight implementation so that it
can easily be used as an environment reporting tool in any Python library with
minimal impact.

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

Use Scooby's `investigate` method to generate `Report` objects. These objects
have representation methods implemented so that if outputted, they show
a nicely formatted report but you could also capture the report as an object
itself.

```py
>>> import scooby
>>> scooby.investigate()
```
```
------------------------------------------------------
  Date: Tue Jun 25 16:17:46 2019 MDT
  Platform: Darwin-18.5.0-x86_64-i386-64bit

             12 : CPU(s)
         x86_64 : Machine
          64bit : Architecture
        32.0 GB : RAM

  3.7.3 | packaged by conda-forge | (default, Mar 27
  2019, 15:43:19)  [Clang 4.0.1
  (tags/RELEASE_401/final)]

         1.16.3 : numpy
          1.3.0 : scipy
          7.5.0 : IPython
          3.1.0 : matplotlib

  Intel(R) Math Kernel Library Version 2018.0.3
  Product Build 20180406 for Intel(R) 64
  architecture applications
------------------------------------------------------
```

But you can also add addtional packages too if you'd like via the `addtional`
keyword argument:

```py
>>> scooby.investigate(additional='pyvista')
```
```
------------------------------------------------------
  Date: Tue Jun 25 16:18:01 2019 MDT
  Platform: Darwin-18.5.0-x86_64-i386-64bit

             12 : CPU(s)
         x86_64 : Machine
          64bit : Architecture
        32.0 GB : RAM

  3.7.3 | packaged by conda-forge | (default, Mar 27
  2019, 15:43:19)  [Clang 4.0.1
  (tags/RELEASE_401/final)]

         1.16.3 : numpy
          1.3.0 : scipy
          7.5.0 : IPython
          3.1.0 : matplotlib
         0.20.4 : pyvista

  Intel(R) Math Kernel Library Version 2018.0.3
  Product Build 20180406 for Intel(R) 64
  architecture applications
------------------------------------------------------
```

Or maybe you want a whole bunch of additional packages:

```py
>>> scooby.investigate(additional=['pyvista', 'vtk', 'appdirs',])
```
```
------------------------------------------------------
  Date: Tue Jun 25 16:18:16 2019 MDT
  Platform: Darwin-18.5.0-x86_64-i386-64bit

             12 : CPU(s)
         x86_64 : Machine
          64bit : Architecture
        32.0 GB : RAM

  3.7.3 | packaged by conda-forge | (default, Mar 27
  2019, 15:43:19)  [Clang 4.0.1
  (tags/RELEASE_401/final)]

         1.16.3 : numpy
          1.3.0 : scipy
          7.5.0 : IPython
          3.1.0 : matplotlib
         0.20.4 : pyvista
          8.2.0 : vtk
          1.4.3 : appdirs

  Intel(R) Math Kernel Library Version 2018.0.3
  Product Build 20180406 for Intel(R) 64
  architecture applications
------------------------------------------------------
```


Want to add a package to investigate but aren't sure if it is present,
simply define the `optional` list in the arguments. Note that the default
libraries of `numpy`, `scipy`, `IPython`, and `matplotlib` are defaults for
optional argument, so you might want to put those in the `core` argument if
you care about those.

```py
>>> scooby.investigate(core=['numpy', 'matplotlib'], optional=['foo', ])
```
```
------------------------------------------------------
  Date: Tue Jun 25 17:51:30 2019 MDT
  Platform: Darwin-18.5.0-x86_64-i386-64bit

             12 : CPU(s)
         x86_64 : Machine
          64bit : Architecture
        32.0 GB : RAM

  3.7.3 | packaged by conda-forge | (default, Mar 27
  2019, 15:43:19)  [Clang 4.0.1
  (tags/RELEASE_401/final)]

         1.16.3 : numpy
          3.1.0 : matplotlib

  Intel(R) Math Kernel Library Version 2018.0.3
  Product Build 20180406 for Intel(R) 64
  architecture applications
------------------------------------------------------
```

Since the `foo` package wasn't found and it's optional, nothing is reported.
But what if you need some sort of error message that a package wasn't found?
Then add your package to the `additional` list and Scooby will let you now it
was not found but like any good pooch, Scooby will complete the investigation:

```py
>>> scooby.investigate(additional=['foo',])
```
```
------------------------------------------------------
  Date: Tue Jun 25 21:23:56 2019 MDT
  Platform: Darwin-18.5.0-x86_64-i386-64bit

             12 : CPU(s)
         x86_64 : Machine
          64bit : Architecture
        32.0 GB : RAM

  3.7.3 | packaged by conda-forge | (default, Mar 27
  2019, 15:43:19)  [Clang 4.0.1
  (tags/RELEASE_401/final)]

         1.16.3 : numpy
          1.3.0 : scipy
          7.5.0 : IPython
          3.1.0 : matplotlib

  RUH-ROH! These modules were either unavailable or
  the version attribute is unknown:

    unavailable : foo

  Intel(R) Math Kernel Library Version 2018.0.3
  Product Build 20180406 for Intel(R) 64
  architecture applications
------------------------------------------------------
```


## Optional Requirements

The following are a list of optional requirements and their purpose:

- `psutil`: report total RAM in GB
- `mkl`: report Intel(R) Math Kernel Library version
