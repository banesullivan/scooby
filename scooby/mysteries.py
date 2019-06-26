"""
Tools fo solving common mysteries.
"""

def in_ipython():
    """Mystery: are we in an IPython environment?

    Note
    ----
    This will return ``True`` in Jupyter environments, so be sure to check
    :func:`scooby.in_jupyter` first

    Returns
    -------
    bool : True if in an IPython environment
    """
    try:
        _ = __IPYTHON__
        return True
    except NameError:
        return False


def in_jupyter():
    """Mystery: are we in a Jupyter environment?

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
