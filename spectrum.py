"""This module is used to construct Spectra. Each Spectrum has a number of
attributes, like `self.nuclide`. `self.frequency`, `self.solvent` and so
forth. All signals are collected into the `self.signals` list, a list of
`Signal` objects, which have attributes on their own, too.

This module can raise `InputError`."""

from exceptions import InputError
from signal import Signal
from block import Block
import writer as w
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from cues import CUES

class Spectrum:
    """The class that defines a spectrum"""

    def __init__(self, r_spectrum, formatter, blocked_signals_only=False):
        """Take in a tuple that contains a cypher and the spectre and run it
        through a formatter to construct a `Spectrum` object

        :param formatter: `Formatter`. Used to parse the spectrum, also this is
        the default format for writing the spectrum.
        """
        self.cypher = r_spectrum[0]     # cypher should be the first element
                                        # of the tuple
        self.formatter = formatter
        # Store the formatter in the `Spectrum` object as well. The
        # formatter is used to parse `self.text` and also is the default
        # format for writing the spectrum.

        if blocked_signals_only:
            self.text = r_spectrum[1]
            self.signals = []
            self.parse_signals()
        # This scenario is triggered when there's a need to build a
        # `Spectrum` with reassignment signals only. In that case, the input
        # will already be a `Block` object, so we simply save it as it is.
        # since the data contains no head, `self.parse_head` method is omitted.

        else:
            self.text = Block(r_spectrum[1], runs=True)
        # the rest of the text should be the second element of the tuple,
        # and we store it as a `Block` object. The correct formatting of
        # each symbol is retained since we construct the `Block` from a
        # paragraph object, and we signal that by using `runs` parameter.

        # If the spectrum is built during the reassigning functionality,
        # Block objects are already there, there's no need to build them.

            self._spectrum_data = []             # raw spectrum data
            self.read()


        # These three attributes store `Block` objects
        self.nuclide = self._spectrum_data[
            self.formatter.head.variables_str.index('%n')] if '%n' in \
                self.formatter.head.variables_str else None
        self.solvent = self._spectrum_data[
            self.formatter.head.variables_str.index('%s')] if '%s' in \
                self.formatter.head.variables_str else None
        self.frequency = self._spectrum_data[
            self.formatter.head.variables_str.index('%f')] if '%f' in \
                self.formatter.head.variables_str else None

    def write(self, document, formatter=None):
        """Write a spectrum to a paragraph using JUSTIFY alignment."""
        _paragraph = document.add_paragraph()
        _paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
        w.print_runs(_paragraph, Block(self.cypher))
        w.format_runs(_paragraph)
        # print and format the cypher

        _paragraph = document.add_paragraph()
        _paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
        if formatter is None:
            formatter = self.formatter
        # Ready to print the spectrum itself. If no formatter is given,
        # use the formatter used to read the spectrum.

        w.build_runs(self, _paragraph, formatter.head)
        for signal in self.signals:
            w.build_runs(self, _paragraph, formatter.hypotheses, signal)
            if self.signals[-1] != signal:
                w.print_runs(_paragraph, formatter.delimiter)
        if formatter.end:
            w.print_runs(_paragraph, formatter.end)
        w.format_runs(_paragraph)
        # Print each signals, separating those with a given delimiter. Use
        # the end symbol if one is provided. Use the same paragraph for
        # printing.

    def read(self):
        """Parse the spectrum text using a formatter, fill in
        `self.nuclide`, `self.frequency`, `self.solvent` and `self.signals`"""
        self.signals = []
        self.parse()

    def parse(self):
        """Combine the two parse methods into one."""
        self.parse_head()
        self.parse_signals()

    def parse_head(self):
        """
        Parse the head section of the spectrum using `self.formatter.head`.
        """

        for block in self.formatter.head.constants:
            if block not in self.text:
                raise InputError(f'"{block()}", given in the format '
                                 f'template, is never ecnountered in the '
                                 f'spectrum {self.cypher}')
                # raise an InputError if the input is missing constant
                # information given in the formatter.
            _i = self.text.index(block)
            # remember the position of the located blocks.
            if self.text[:_i]:
                _variable = self.text[:_i]
                self._spectrum_data.append(Block(_variable))
            # if there's anything prior to that position, it's an unparsed
            # variable to be stored
            _temp = self.text[_i + len(block()):]
            self.text = _temp
            # cut away the parsed portion of the text

    def parse_signals(self):
        """
        Parse the signal section of the spectrum.
        :return: None.
        """
        _delimiter = self.formatter.delimiter
        # _delimiter is the actual delimiter specified by the user.
        delimiter = self.formatter.signals()[-1]() + _delimiter \
            if not self.formatter.signals()[-1].variable and \
               not self.formatter.signals()[-1].optional else _delimiter
        # if the final character in repeats is not optional or variable,
        # that's a good cue for splitting. `self.formatter.signals` is called
        # here so as to make it subscriptible.

        # delimiter = _delimiter # a line I like to use to trigger
        # `self.complex_parse_into_signals(delimiter)`
        # if delimiter() not in self.text():
        #     raise InputError(f'"{delimiter()}" не встречается в тексте '
        #                      f'сигнала, поэтому невозможно считать спектр')
        # If the said delimiter is absent from the self.text (which now only
        # contains the signals), raise an InputError.
        # Currently disabled, since cases with only one signal raise
        # this error.

        if delimiter() not in ''.join(self.formatter.hypotheses()[0][0].str):
            _signals = self.text.split(delimiter)
            for i, signal in enumerate(_signals):
                _signals[i].pop() if signal[-1]() in self.formatter.end() \
                    else None
                if self.formatter.signals.constants and \
                        self.formatter.signals.section:
                    _signals[i] += self.formatter.signals.constants_str[-1] if \
                        not self.formatter.signals.constants[-1].optional and \
                        self.formatter.signals.constants[-1] == \
                        self.formatter.signals.section[-1] and \
                        self.formatter.signals.constants_str[-1] != signal[-1]() \
                        else ''
            # If the fullest hypothesis (`self.formatter.hypotheses()[0][0]`)
            # does not contain the delimiter, then it's unique to margins
            # between each signal. We can simply split the text Block into
            # smaller Blocks. But that will also clip the ending of each
            # signal, plus the final period, if there, will be parsed as part
            # of the final signal. So first we clip the  period
            # (`self.formatter.end()`) if it's there, then we add the closing
            # character(s) to each signal if they're not optional, and indeed
            # are at the end of the signal, and are not already there in the
            # signal.

        else:
            _signals = self.complex_parse_into_signals(delimiter)
            # If the easy parsing can't be performed, do the hard-guessing.

        for signal in _signals:
            #print(f"{signal()}") # uncomment this to find irregularities in
            # text format
            hypothesis = self.match_hypothesis(signal)
            self.signals.append(self.parse_signal(signal, hypothesis))
            # For each signal, match it with its best-fitting hypothesis and
            # use that to parse it.

    def complex_parse_into_signals(self, delimiter):
        """Executed when the delimiter between signals is also encountered
        within the signals. Probably some of the logics could be enhanced,
        but at this point I haven't run into any bugs (but I still might)

        :return: a list of signal Blocks"""
        _signals = []
        finished = False
        # `while` Loop flag

        while not finished and self.text:
        # read "as long as we still have options and there're things to parse"

            l_anchor = self.formatter.signals.constants[0]
            r_anchor = self.formatter.signals.constants[-1]
            # anchors within a signal to help find its margins. Begin with
            # the first and last constant Blocks within a repeat.

            i = 1
            while l_anchor not in self.text and i < \
                    len(self.formatter.signals.constants):
                l_anchor = self.formatter.signals.constants[i]
                i += 1
            # if it so happens that the current `l_anchor` is altogether
            # absent, keep trying to match the next ones until everything
            # has been tried

            # Idea: maybe also check that the anchor is not equal to the
            # delimiter? And instead of just checking for constants,
            # check it for obligatory constants specifically?

            i = -2
            while r_anchor not in self.text and i >= \
                    -len(self.formatter.signals.constants) and \
                    self.formatter.signals.constants.index(r_anchor) >= \
                    self.formatter.signals.constants.index(l_anchor):
                r_anchor = self.formatter.signals.constants[i]
                i -= 1
            # if it so happens the the current `r_anchor` is altogether
            # absent, keep trying to match the next ones until everything
            # has been tried, or until `r_anchor` points at the same Block as
            # `l_anchor`.

            if (l_anchor not in self.text and r_anchor not in
                    self.text) \
                    or (l_anchor == delimiter and r_anchor == delimiter) or \
                    delimiter() not in self.text():
                _signals.extend(self.text.split(delimiter))
                finished = True
            # if neither of the anchors have still been found within the
            # text, or both of them are the same as the delimiter, or the
            # delimiter itself is absent, just try the auto-splitting and
            # call it a day.

            else:
                while l_anchor in self.text and r_anchor in self.text \
                        and delimiter in self.text:
                    # Keep this loop going as long as the three identifiers
                    # can be located. Once they can't, end the loop, and that
                    # will result in the auto-splitting of what's left as used
                    # above.

                    text_ = self.text[:] # temp copy of self.text Block.
                    _l_anch_index = self.text.index(l_anchor) \
                        if l_anchor != delimiter else \
                        self.text.index(r_anchor)
                    # use `l_anchor` as an actual left anchor as long as
                    # it's not the same as the delimiter.

                    _r_anch_index = self.text.index(r_anchor) \
                        if r_anchor != delimiter else \
                        self.text.index(l_anchor)
                    # use `r_anchor` as an actual right anchor as long as
                    # it's not the same as the delimiter.

                    # Idea: Maybe think of a strategy if both `l_anchor` and
                    # `r_anchor` fail?

                    if self.text.index(delimiter) < _l_anch_index:
                        _l_index = len(self.text) - self.text[::-1].index(
                            delimiter, self.text[::-1].index(l_anchor))
                        # if the delimiter is encountered before the anchor,
                        # then the left margin is the end of the first
                        # delimiter before the anchor (which is not
                        # necessarily the same as the first delimiter in
                        # `self.text`)
                    else:
                        _l_index = None
                        # Otherwise `_l_index` is the first element.

                    if delimiter in \
                            self.text[_r_anch_index + len(r_anchor):]:
                        _r_index = self.text.index(delimiter,
                            _r_anch_index + len(r_anchor))
                        # If there're delimiters after the right anchor,
                        # then the first of those delimiters will be use as
                        # right index.
                    else:
                        _r_index = None
                        # Otherwise the slicing will be made up until the
                        # end of list.

                    _signals.append(self.text[_l_index:_r_index])
                    self.text = self.text[len(_signals[-1]) + len(delimiter):]
                    # Append the slice, and extract it from `self.text`.

                    if self.text == text_:
                        finished = True
                        break
                    # If by this time the strategy is not working,
                    # then there's nothing to be done and the function
                    # should conclude.

        return _signals

    def match_hypothesis(self, signal):
        """
        Match the right hypothesis to interpret a signal. Start with the
        longest hypothesis and work from there. If each of the constant
        Blocks in the hypothesis can be found, no shorter hypothesis will
        be checked. If each constant Block is found only once, that is the
        right hypotheses. Otherwise, assess the ambiguity of a hypothesis by
        the number of times each of the Blocks is encountered and return the
        hypothesis with the fewest count.

        :param signal: `Block` object, contains raw signal data.
        :return: `Section` object, containing a list of Blocks from matched
        hypothesis.
        """

        for hypothesis_set in self.formatter.hypotheses():
            scores = []
            # scores are relevant only within a set of hypotheses of the same
            # length

            for hypothesis in hypothesis_set:
                if not hypothesis.constants: # If the entire hypothesis is
                    # just one variable, that's the correct hypothesis
                    return hypothesis
                score = 0
                next_ = False # trigger to tell us that the hypothesis is wrong
                counts = []
                _temp = signal[:]
                for block in hypothesis.constants_str:
                    count = _temp.count(block)
                    if count == 0: next_ = True; break
                    # if a Block from the hypothesis can't be found,
                    # the hypothesis is false, stop checking Blocks.
                    counts.append(count)
                    _temp = _temp[_temp.index(block):]
                    # otherwise remember the count and clip the signal

                if next_:
                    scores.append(-1)
                    continue
                    # If the hypothesis is wrong, record its count as -1 and
                    # move on to the next hypothesis
                if set(counts) == {1}:
                    return hypothesis
                    # If a hypothesis has exactly one of each `Block`,
                    # that's a bingo.
                for count in counts:
                    score += count - 1
                    scores.append(score)
                    # Else score a penalty point for each extra encounter of
                    # a `Block` and write that to scores

            # Next evaluate each of the scores. First of all, negative
            # scores are scores of false hypotheses, we should not include
            # those. Then find the minimal score. The first hypothesis with
            # that score will be the working one.
            _scores = []
            for score in scores:
                if score >= 0:
                    _scores.append(score)
            if not _scores:
                continue
            # If all hypotheses of current length have been neglected,
            # the `_scores` list will be empty, we should consider shorter
            # hypotheses.

            _hypothesis = hypothesis_set[scores.index(min(_scores))]
            return _hypothesis
            # Choose the hypothesis with the minimal penalty score.

        raise InputError('the text cannot be matched with the input format '
                         'template')
        # If no hypothesis has been matched up until now, then raise
        # InputError, since it doesn't match the format template.

    def parse_signal(self, signal, hypothesis):
        """Parse a signal using a matched hypothesis and return a list of
        signal variables

        :param signal: a signal `Block`.
        :param hypothesis: a hypothesis `Section`.
        :return: `Signal` object.
        """
        _signal_variables = []

        # If the signal only has one variable with no constants, just feed
        # the signal to the `Signal` class.
        if len(hypothesis.variables) and not hypothesis.constants:
            return Signal([signal], hypothesis)

        for i, block in enumerate(hypothesis.constants_str):

            temp_block_i = signal.index(block)
            # Find its place within the signal

            # If that's not the final block, then make a slice of the signal
            # up until the first occurrence of the next `Block` after
            # current block. Then find the last occurrence of the current
            # `Block` within the slice. In other words, when there're
            # several occurrences of the same block, assume that the latest
            # before the next sort of `Block` is the one to use.
            if i < len(hypothesis.constants_str) - 1:
                sliced_list = signal[:signal.index(
                    hypothesis.constants_str[i+1], temp_block_i + len(block))]
            else:
                sliced_list = signal[:]

            sliced_list.reverse()
            block_i = sliced_list.index(block[::-1])
            true_block_i = len(sliced_list) - block_i - len(block)
            working_slice = signal[:true_block_i]
            working_slice.lstrip()

            # If there's anything in that slice at all, add it to the signal.
            if working_slice:

                # Load the cue for the currently sought-for signal.
                cue = CUES[hypothesis.variables[len(_signal_variables)]()]
                appendix = Block()
                if cue is None:
                    appendix = working_slice
                # If there's no cue for the sought variable, just assume the
                # working slice is the variable.

                else:
                    while working_slice:
                        if working_slice[0]() in cue:
                            appendix.append(working_slice[0])
                            del working_slice[0]
                            # Parse only those chars that are confirmed by
                            # the cue

                        elif block in working_slice[:len(block)]:
                            break
                        # if a currently worked constant Block is encountered
                        # several times within the `working_slice` and
                        # there're chars withing the `working_slice` that
                        # don't meet the `CUES` requirement, interpret the
                        # `working_slice` as having several variables within
                        # it to be parsed, with the first instance of the
                        # currently worked Block as the delimiter (since
                        # breaking the loop will result in storing the
                        # parsed variable and clipping the first instance of
                        # `block`).

                        else:
                            raise InputError(f'Spectrum {self.cypher} cannot '
                                             f'be parsed')
                        # If all else fails, something is wrong with the
                        # input text, not the code. (run into this error way
                        # too many times to only later find out that the input
                        # file wasn't correct, and the code was just fine)
                        # Idea: have the error message specify which block
                        # of text from the input file causes the issue.

                _signal_variables.append(appendix)
            signal = signal[len(appendix) + len(block):]
            # clip the signal for the amount of the processed `Block`

        return Signal(_signal_variables, hypothesis)
        # Feed the collected variables and the hypothesis to instance a
        # correct `Signal` object.

    def __str__(self):
        nuclide = f'nuclide {self.nuclide()}, ' if self.nuclide else ''
        solvent = f'solvent {self.solvent()}, ' if self.solvent \
            else ''
        frequency = f'machine frequency {self.frequency()}, ' \
                    if self.frequency \
            else ''
        signals = f'{len(self.signals)} signals.'

        return (f'Spectrum {self.cypher}: ' + nuclide + solvent + frequency +
                signals)
