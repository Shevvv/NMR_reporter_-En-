"""
This module is for writing down processed spectra into a .docx files with
correct styling.
"""

from exceptions import FormatError
from docx.shared import Pt


def build_runs(spectrum, paragraph, formatter, signal=None):
    """Since text styling is done with `Run` objects in .docx, assemble
    those from each indivifual block in the formatter"""

    def match_hypothesis(signal, formatter):
        """Find the hypothesis that shares the same set of variables as the
        currently written `Section`"""

        for hypothesis_set in formatter.hypotheses:
            for hypothesis in hypothesis_set:
                if hypothesis.contains <= signal.hypothesis.contains:
                    return hypothesis
        raise FormatError('the output format requires data the input spectra'
                          'do not provide')
        # The function allows hypotheses to be too short to the relevant
        # `Signal` data (if you want to have the output to store less
        # information than the input), but never too full (since the
        # respective data will simply not be there in the input).

    if signal:
        formatter = match_hypothesis(signal, formatter)
    # Only signals need to be matched against hypotheses since there might
    # be some optional data.


    for block in formatter():
        if '%' in block:
            variable = match_variable(spectrum, block, signal=signal)
            # The '%' special symbols signals that the block is variable,
            # this has to be matched with its value for this signal.

            if not variable:
                raise FormatError(f'spectrum "{spectrum.cypher}" does not '
                                  f'provide the data required by the output '
                                  f'format template')
            # Pretty sure this piece of code is redundant since the
            # `match_hypothesis` function already checks for it, but just in
            # case, let it stay.
            # Idea: this one specifies which spectrum causes the problem,
            # Looks like it's a more preferable error message than the
            # simple `your output format is too excessive`.

            print_runs(paragraph, variable)
            # Print the variable using the styling stored in the spectrum.

        else:

            print_runs(paragraph, block)
            # Print the constant block using the styling provided by the
            # output format.


def print_runs(paragraph, block):
    """A function that checks whether a single block is to be written down
    as just one or many `Run` objects"""

    for i, char in enumerate(block):
        if i == 0:
            run = paragraph.add_run(char())
            style_run(run, char)
            # The first char within the block always initiates a new `Run`,
            # and its styling is defined

        elif char.bits != block[i-1].bits:
            run = paragraph.add_run(char())
            style_run(run, char)
            # The same goes for a char whose styling doesn't match that of a
            # previous char. Can't combine it with a previous `if`
            # expression since this one requires there to be a previous char
            # in the first place.

        else:
            run.text += char()
            # If the styling maintains, just add the char to the run.

def style_run(run, char):
    """Define the styling of a run from the styling of the first char in it."""

    run.italic = char.bits[0]
    run.bold = char.bits[1]
    run.underline = char.bits[2]
    run.font.subscript = char.bits[3]
    run.font.superscript = char.bits[4]

def format_runs(paragraph):
    """
    Format a paragraph as Pt 14 Times New Roman.
    Idea: maybe make it customizable by the user?
    """

    for run in paragraph.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)


def match_variable(spectrum, block, signal=None):
    """
    A simple function for matching a special notation of a variable to it
    value within the spectrum/signal.

    :param spectrum: the `Spectrum` object with data to be matched.
    :param block: the special notation of a variable to be matched.
    :param signal: the `Signal` object with data to be matched. If data to
    be matched is from the head of the spectrum and not the signal, it's set
    to `None`.

    :return: the value of the variable within the spectrum/signal matching
    the `block` special notation.
    """

    if "%n" in block:
        return spectrum.nuclide
    if "%s" in block:
        return spectrum.solvent
    if "%f" in block:
        return spectrum.frequency
    if not signal:
        raise FormatError(f'"{block()}" cannot be used in the head of the '
                          f'spectrum!')
    if "%c" in block:
        return signal.chemshift
    if "%i" in block:
        return signal.integral
    if "%m" in block:
        return signal.multiplicity
    if "%j" in block:
        return signal.j_values
    if "%a" in block:
        return signal.assignment