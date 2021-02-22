"""A module containing a single `Signal` class for representing a signal"""
from block import Block

class Signal:
    """A class for representing a single signal: it's chemical shift,
    integral, multiplicity, J values and assignment."""

    def __init__(self, signal_variables, hypothesis):
        """Initiate a `Signal` object from a list of Blocks and a matched
        hypothesis to build correspondences."""
        self.hypothesis = hypothesis

        self.chemshift = signal_variables[
            self.hypothesis.variables_str.index('%c')] if '%c' in \
            self.hypothesis.variables_str else None
        self.integral = signal_variables[
            self.hypothesis.variables_str.index('%i')] if '%i' in \
            self.hypothesis.variables_str else None
        self.multiplicity = signal_variables[
            self.hypothesis.variables_str.index('%m')] if '%m' in \
            self.hypothesis.variables_str else None
        self.j_values = signal_variables[
            self.hypothesis.variables_str.index('%j')] if '%j' in \
            self.hypothesis.variables_str else None
        self.assignment = signal_variables[
            self.hypothesis.variables_str.index('%a')] if '%a' in \
            self.hypothesis.variables_str else Block('')


    def __str__(self):
        chemshift = f'Chemshift: {self.chemshift()}' if self.chemshift else ''
        integral = f', integral: {self.integral()}' if self.integral else ''
        multiplicity = f', multiplicity: {self.multiplicity()}' \
                       if self.multiplicity else ''
        j_values = f', J constant(s): {self.j_values()} Hz' if self.j_values \
            else ''
        assignment = f', assignment: {self.assignment()}' if self.assignment \
                     else ''
        return (chemshift + integral + multiplicity + j_values +
                assignment) + '.'
