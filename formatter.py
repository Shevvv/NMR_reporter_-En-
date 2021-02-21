"""
This module is for handling format templates. As with any input from a
`.docx` file, it works with `Block` objects, which are pretty much
lists of `Char` objects. `Formatter` class has some nested classes in it,
namely `Section` and `Hypotheses`.

`Section` class stores higher level elements of the format template, such as
the head or the signal. A single hypothesis, pretty much a version of a
signal format, is also stored as a `Section` object.

`Block` objects are the elements of `Sections`, and they store such
attributes as whether the block is constant or variable, optional or
obligatory, and so on. `Section` class is capable of reading those
attributes and collecting blocks with the same attribute values together into
separate lists.

`Hypotheses` object acts as a two-dimensional list of all the hypotheses
derived from the format template. The first dimension unites sorted hypotheses
by their length, from fullest to shortest. The idea is that a fuller
hypothesis should be chosen over a shorter one. As mentioned earlier,
each individual hypothesis is an instance of a `Section` class.

This module can raise `FormatError`.
"""


from exceptions import FormatError
from block import Block
from cues import CUES


class Formatter:
    """Class for interpreting format templates. Since the style of a format
    matters, it operates in `Block` instances. The three central
    attributes are `self.head`, `self.signals` and `self.hypotheses`. The
    first two are `Section` objects, containing sequences of Blocks,
    which are composed of Chars. `self.hypotheses` is a `Hypotheses` object,
    a list of lists of `Section` objects."""

    def __init__(self, raw_nmr_format):
        """Build a `Formatter` object, containing `self.head`,
        `self.signals` and `self.hypotheses`.

        :param raw_nmr_format: `Block` object built from the format
        template inside a `.docx` file.
        """

        self._raw_nmr_format = raw_nmr_format  # temporarily store the raw data
        if self._raw_nmr_format.count('/') != 3:
            raise FormatError('there must be three and only three slashes ('
                              '"/" in a format template!')
        # There should always be three and only 3 slashes in the input
        if self._raw_nmr_format.count('*') % 2 != 0:
            raise FormatError("there's an odd number of optionality markers "
                              "('*').")
        # Since an asterisk ("*") is used to enclose optional blocks,
        # there should always be an even number of those.

        self._repeat_i = self._raw_nmr_format.index('/')
        # Find the position where the repeats begin
        self._repeat_i2 = self._raw_nmr_format.index('/',
            self._repeat_i + 1)
        # and end
        self._repeat_i3 = len(self._raw_nmr_format) - 1 - \
                          self._raw_nmr_format[::-1].index('/')
        # and also where the delimiter ends

        if self._raw_nmr_format[self._repeat_i - 1] != ' ':
            raise FormatError('there must be a whitespace before the first '
                              'instance of "/"')
        # The repeats should always be preceded with a whitespace.
        self._head = self._raw_nmr_format[:self._repeat_i]
        # Raw version of `self.head` runs up until the first slash.
        self._signals = self._raw_nmr_format[self._repeat_i + 1:
                                             self._repeat_i2]
        # From there to the second slash is the raw signals template. Slash
        # itself is excluded.
        self.delimiter = self._raw_nmr_format[
            self._repeat_i2 + 1:self._repeat_i3]
        # then comes the delimiter, with slash once again excluded.
        if self._repeat_i3 != len(self._raw_nmr_format) - 1:
            self.end = Block(self._raw_nmr_format[-1])
        else:
            self.end = Block()
        # If it so happens that the third slash is not the last symbol in
        # the format template, then interpret everything after it as the
        # end. Either way, there must be `self.end`, a Block object.

        self.head = self.Section(self._parse(self._head))
        self.signals = self.Section(self._parse(self._signals))
        self.hypotheses = self.Hypotheses(self.signals)
        # Build the three central attributes from their raw versions.

    def _parse(self, unparsed):
        """Parses the head or signals format template into a list of
        functional Blocks, which is then returned to be contained in a
        `Section` object."""
        _text = Block()    # Text should be stored as a list of `Char`
                                # objects, which means using a `Block`
                                # container.
        _optional = False       # On default, each block is considered
                                # obligatory.
        list_of_parsed = []     # List to contain readied `Block` objects.
        while unparsed:         # As long as there's anything unparsed...
            if unparsed[0]() not in ('%', '*'):     # `unparsed` is a
                                                    # `Block` object,
                                                    # while indexed it returns
                                                    # a `Char` object, which,
                                                    # when called, returns
                                                    # a string representation
                                                    # of itself.
                _text.append(unparsed[0])   # Append a `Char` if it's not
                del unparsed[0]             # special, then move on to the next
                continue                    # `Char` object.
            if _text(): list_of_parsed.append(Block(_text,
                _optional))
            _text = Block()         # This code is only be executed if a
                                    # special symbol has been encountered.
                                    # `_text()` evaluation is necessary since
                                    # the first `Char` in the `unparsed` could
                                    # have been optional, resulting in ''.
            if unparsed[0] == '%':
                _key = '%' + unparsed[1]().lower()  # '%' is always followed
                                                    # by just one symbol, so
                                                    # that is combined together
                                                    # in `_key`, a str.
                if self._raw_nmr_format.count(_key) > 1:
                    raise FormatError(f'"{_key}" is encountered more than '
                                      f'once in the format template!')
                # The same key is not allowed twice

                if list_of_parsed:
                    if '%' in list_of_parsed[-1]():
                        raise FormatError('two special notations are not '
                                          'separated with a whitespace in '
                                          'the format template!')
                # Nor should they be consequent

                if _key not in CUES:
                    raise FormatError(f'special notation "{_key}" cannot '
                                      f'be recognized')
                # Only predefined keys are allowed

                for _ in range(2): del unparsed[0]
                list_of_parsed.append(Block(_key, _optional,
                    variable=True))
                # Build a key `Block` through `variable=True` parameter

            elif unparsed[0] == '*':    # Lastly, margins for optional Blocks
                                        # are processed
                # if not list_of_parsed or len(unparsed) == 1:
                #     raise FormatError('знак опциональности "*" находится с '
                #                       'краю шаблона формата')
                # If nothing has been parsed yet, or '*' is the last symbol
                # to be parsed, it means '*' is at the edge of template
                # format, which is not allowed. (currently inactive)
                _optional = not _optional   # switch the `_optional` cue
                list_of_parsed.append(Block('', _optional))
                del unparsed[0] # '' is a cue `Hypotheses` class can easily
                                # identify to break Sections into optional and
                                # obligatory parts.
        if _text(): list_of_parsed.append(Block(_text, _optional))
        return list_of_parsed
        # this code is executed after the loop. If the final character was
        # constant, it'll not trigger `Block` instancing, so that line is
        # repeated here.

    class Section:
        """A class for storing lists of `Blocks`. Doing it this way allows
        to group `Blocks` depending on their attributes."""

        def __init__(self, section, contains=None):
            """Build a `Section` from a list of Blocks. A list of variables
            can also be provided
            """
            self.section = section # The actual list object
            self.str = [block() for block in self.section]
            # the same list but made of str objects

            self.constants = [x for x in self.section if not x.variable]
            self.constants_str = [constant() for constant in self.constants
                if constant() != '']
            # excerpts of the two lists above with only constant Blocks

            self.variables = [x for x in self.section if x.variable]
            self.variables_str = [variable() for variable in self.variables
                if variable() != '']
            # variable only

            self.obligatories = [x for x in self.section if not x.optional]
            self.obligatories_str = [obligatory() for obligatory in
                self.obligatories if obligatory() != '']
            # obligatory only

            self.optionals = [x for x in self.section if x.optional]
            self.optionals_str = [optional() for optional in self.optionals
                if optional() != '']
            # optional only

            self.contains = contains
            # this lists all the variable info contained within the
            # `Section`, used to choose between different hypothesis sections.

        def splice_blocks(self):
            """This method is used to splice adjacentBlocks with same
            `variable` attribute"""

            for i, block in enumerate(self.section):
                if i - 1 >= 0:
                    if block.variable == self.section[i-1].variable:
                        self.section[i-1] = self.section[i-1] + block
                        self.section[i] = Block('', variable=None)
            for item in self.section[:]:
                if item == Block('', variable=None):
                    self.section.remove(item)
            self.__init__(self.section, contains=self.contains)

        def __call__(self):
            return self.section
        # Calling a `Section` makes it subscriptable, iterable and so forth.

    class Hypotheses:
        """A class that contains all the possible sequences of blocks in a
        signal. The main attribute `self.hypotheses` is a two-dimensional
        list. Lists of individual hypotheses are grouped together judging by
        their length, each group is then listed in the order of decreasing
        lengths. This way it's easy to choose a longer hypothesis over a
        shorter one."""

        def __init__(self, signal):
            """Only the `Formatter.signals` is used to build Hypotheses"""
            self._pieces = []
            _piece = []

            for block in signal():
                if block() == '':
                    self._pieces.append(_piece)
                    _piece = []
                else:
                    _piece.append(block)
            if _piece: self._pieces.append(_piece)
            # The signal is broken down into Blocks, Blocks are grouped into a
            # `_piece` depending on whether they're optional or not. In the
            # resulting `self._pieces` list the first group of Blocks is
            # always obligatory. "''" is the cue for where the switch
            # between optional/obligatory happens. At the margin, append the
            # current `self._piece` to the list of pieces `self._pieces`.

            self.hypotheses = []
            for n in range(len(self._pieces[1::2]) + 1):
                self.build_hypotheses(n)
                # len(self._pieces[1::2]) shows the number of optional
                # pieces, `+ 1` ensures that there's the hypothesis with all
                # pieces in there.

            self.hypotheses.reverse()
            # The resulting list has hypotheses in order of increasing
            # lengths, which is the reverse of the desired result.

        def build_hypotheses(self, n):
            """Build a list of all the hypotheses that have exactly n
            optional pieces in them. Append the resulting list to
            `self.hypotheses`. Doesn't return anything"""

            def find_combinations(a_list, n):
                """Find all combinations of `n` optional pieces to be added to
                a hypothesis. Return a two-dimensional list: list of
                combinations, where each combination is a list of
                optional pieces (which in turn is a list of Blocks)."""

                leftout = [x for x in range(n, len(a_list))]
                # `leftout` is a list of indices that will be used to knock
                # out excluded pieces. It starts with a list of consequent
                # indices, corresponding to the final elements of the list.
                if not leftout:
                    return [a_list]
                # If nothing is to be leftout, conclude the execution of the
                # function. `a_list` is nested in a list to conform to the
                # format of any other function return.
                combinations = []
                # Otherwise, begin building combinations.
                while True:
                    finished = True
                    # Enter the loop with the presumption that this is the
                    # last iteration.
                    temp_list = [x for x in a_list]
                    # Soft copy the pieces into a temporary list
                    for i, item in enumerate(a_list):
                        if i in leftout:
                            temp_list.remove(item)
                    combinations.append(temp_list)
                    # Exclude all the items whose indices are listed in the
                    # `leftout`, then try to make a new iteration of `leftout`.
                    if leftout[0] > 0:
                        leftout[0] -= 1
                        continue
                        # If the first index hasn't reached 0, subtract 1.
                        # That's it, new iteration ready, start a new loop.
                    for i, item in enumerate(leftout):
                        if item - 1 not in leftout and i != 0:
                            leftout[i] -= 1
                            finished = False
                            for index in reversed(range(len(leftout[:i]))):
                                leftout[index] = leftout[index + 1] - 1
                            break
                            # if there's a gap between any of the indices
                            # ones after the first index has reached 0,
                            # decrement the first index after the first gap
                            # and set each index to the left of the
                            # decremented one consequently. Only one index
                            # should be decremented at a time, so the loop
                            # is broken, `finished = False` signals that
                            # there's at least one more iteration to do.
                    if finished:
                        return combinations
                        # if up until this point nothing managed to signal
                        # that they're still some iterations left, conclude
                        # the execution of the function.

            combinations = find_combinations(self._pieces[1::2], n)
            # Build a list of all combinations containing exactly `n`
            # optional pieces.
            self._hypotheses = []
            # Ready a temporary list that will store all hypotheses of the
            # same length

            for combination in combinations:
                self._hypothesis = []
                # Ready an empty hypothesis
                for piece in self._pieces:
                    if self._pieces.index(piece) % 2 == 0:
                        self._hypothesis.extend(piece)
                        # Each odd piece is obligatory, so append its Blocks
                        # to the hypothesis.
                    else:
                        if piece in combination:
                            self._hypothesis.extend(piece)
                            # For the optional pieces, only append their
                            # Blocks if they're in the combination.

                _contains = set()
                for block in self._hypothesis:
                    if block.variable:
                        _contains.add(block())
                # Build a set of all the variables that made it into the
                # hypothesis

                hypothesis = Formatter.Section(self._hypothesis,
                    contains=_contains)
                # Build a hypothesis as a `Section` object
                hypothesis.splice_blocks()
                # Splice constant pieces together, and variable pieces
                # tohether. This is needed since orginally there might have
                # been a `''` Block between two constant Blocks. With those
                # removed, constant Blocks need to be spliced.

                self._hypotheses.append(hypothesis)
            self.hypotheses.append(self._hypotheses)
            # When all hypotheses of the same length have been constructed,
            # append them as a single list to `self.hypotheses`.

        def __call__(self):
            return self.hypotheses
            # Calling a `Hypotheses` makes it subscriptable, iterable and so
            # forth.

