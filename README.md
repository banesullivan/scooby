# scooby

[![Build Status](https://travis-ci.org/banesullivan/scooby.svg?branch=master)](https://travis-ci.org/banesullivan/scooby)

A Great Dane turned Python environment detective

Scooby has rich formatting for Jupyter notebooks and rich text formatting for
just about every other environment.

This work is derived from [Dieter Werthmüller](https://github.com/prisae)'s work
towards creating a version reporting tool for the [empymod](https://github.com/empymod/)
and [SimPEG](https://github.com/simpeg/) projects.
This package has been altered to create a lightweight, pure Python
implementation with no non-standard dependencies so that it can easily be used
as an environment reporting tool in any Python library with minimal impact.

## Useage

This is a toolset to easily report your Python environment's package versions
and hardware resources. Usage is simply:

```py
>>> import scooby
>>> scooby.Versions()

------------------------------------------------------
  Tue Jun 25 13:10:46 2019 MDT

         Darwin : OS
             12 : CPU(s)
         1.16.3 : numpy
          1.3.0 : scipy
          7.5.0 : IPython
          3.1.0 : matplotlib

  3.7.3 | packaged by conda-forge | (default, Mar 27
  2019, 15:43:19)  [Clang 4.0.1
  (tags/RELEASE_401/final)]

  Intel(R) Math Kernel Library Version 2018.0.3
  Product Build 20180406 for Intel(R) 64
  architecture applications
------------------------------------------------------
```

But you can also add addtional packages too if you'd like via the `addtional`
keyword argument:

```py
>>> scooby.Versions(additional='pyvista')

------------------------------------------------------
  Tue Jun 25 13:13:37 2019 MDT

         Darwin : OS
             12 : CPU(s)
         1.16.3 : numpy
          1.3.0 : scipy
          7.5.0 : IPython
          3.1.0 : matplotlib
         0.20.4 : pyvista

  3.7.3 | packaged by conda-forge | (default, Mar 27
  2019, 15:43:19)  [Clang 4.0.1
  (tags/RELEASE_401/final)]

  Intel(R) Math Kernel Library Version 2018.0.3
  Product Build 20180406 for Intel(R) 64
  architecture applications
------------------------------------------------------
```

Or maybe you want a whole bunch of additional packages:

```py
>>> scooby.Versions(additional=['pyvista', 'vtk', 'appdirs',])

------------------------------------------------------
  Tue Jun 25 13:14:52 2019 MDT

         Darwin : OS
             12 : CPU(s)
         1.16.3 : numpy
          1.3.0 : scipy
          7.5.0 : IPython
          3.1.0 : matplotlib
         0.20.4 : pyvista
          8.2.0 : vtk
          1.4.3 : appdirs

  3.7.3 | packaged by conda-forge | (default, Mar 27
  2019, 15:43:19)  [Clang 4.0.1
  (tags/RELEASE_401/final)]

  Intel(R) Math Kernel Library Version 2018.0.3
  Product Build 20180406 for Intel(R) 64
  architecture applications
------------------------------------------------------
```
