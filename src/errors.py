#
#   Create/src/errors.py
#
#   Creator: Aleksander Sapieha (sourceguy68@gmail.com)
#
#   Contributors:
#   Aleksander Sapieha (sourceguy68@gmail.com)
#


class PyCreateError(Exception):
    """Base class for PyCreate language errors."""


class PyCreateSyntaxError(PyCreateError):
    """Invalid PyCreate source syntax."""


class PyCreateNameError(PyCreateError):
    """An unknown variable or API function was referenced."""


class PyCreateRuntimeError(PyCreateError):
    """An error occurred while evaluating a PyCreate program."""
