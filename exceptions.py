"""A module for custom exceptions"""

class FormatError(Exception):
    """This exception type is raised during processing of the format
    template."""

    def __init__(self, message=None):
        self.message = message if message else None

    def __str__(self):
        if self.message:
            return '\nFormat error: {}.'.format(self.message)
        return '\nFormat error.'


class InputError(Exception):
    """This exception type is raised when applying a processed format
    template to the input."""

    def __init__(self, message=None):
        if message: self.message = message

    def __str__(self):
        if self.message:
            return '\nText Input error: {}.'.format(self.message)
        return '\nText Input error.'
