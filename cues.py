"""This module contains the CUES dictionary, specifying all the supported
characters for each of the variables."""

CUES = {
    '%n': None,
    '%s': None,
    '%f': [str(x) for x in range(10)] + ['.'],
    '%c': None, # the hyphen symbol that might be given for a range of
                # chemshifts really screws this part up, so I just leave
                # this without any cues.
    '%i': [str(x) for x in range(10)],
    '%m': ['s', 'd', 't', 'q', 'p', 'x', 'h', 'b', 'r', 'm', '*'],
    '%j': [*[str(x) for x in range(10)], '.', ' ', ','],
    '%a': None,
}