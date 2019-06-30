"""
Tools for solving common mysteries.
"""


def in_ipython():
    """Mystery: are we in an IPython environment?

    Returns
    -------
    bool : True if in an IPython environment
    """
    try:
        __IPYTHON__
        return True
    except NameError:
        return False


def in_ipykernel():
    """Mystery: are we in a ipykernel (most likely Jupyter) environment?

    Warning
    -------
    There is no way to tell if the code is being executed in a notebook
    (Jupyter Notebook or Jupyter Lab) or a kernel is used but executed in a
    QtConsole, or in an IPython console, or any other frontend GUI. However, if
    `in_ipykernel` returns True, you are most likely in a Jupyter Notebook/Lab,
    just keep it in mind that there are other possibilities.

    Returns
    -------
    bool : True if using an ipykernel
    """
    ipykernel = False
    if in_ipython():
        try:
            ipykernel = type(get_ipython()).__module__.startswith('ipykernel.')
        except NameError:
            pass
    return ipykernel
