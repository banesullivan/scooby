"""
Tools fo solving common mysteries.
"""

def in_ipython():
    """Mystery: are we in an IPython environment?

    Note
    ----
    This will return ``True`` in Jupyter environments, so be sure to check
    :func:`scooby.in_ipykernel` first

    Returns
    -------
    bool : True if in an IPython environment
    """
    try:
        _ = __IPYTHON__
        return True
    except NameError:
        return False


def in_ipykernel():
    """Mystery: are we in a ipykernel (most likely Jupyter) environment?

    Warning
    -------
    There is no way to tell if the code is being executed in Jupyter or IPython,
    but this method has a high likely hood of being True if in a Jupyter
    notebook and not IPython.

    Returns
    -------
    bool : True if in a Jupyter environment
    """
    notebook = False
    if in_ipython():
        try:
            notebook = type(get_ipython()).__module__.startswith('ipykernel.')
        except NameError:
            pass
    return notebook
