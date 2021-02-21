"""This module contains class `Block`, which is essentially a list of string
`Char` objects. As such, it has a lot of the same functionality as both
lists and strings, except that it has some useful attributes in it. Class
`Char`, the class to describe the styling of each character, is also defined
here."""


class Block:
    """A class for describing a sequence of styled characters. Acts a lot
    like a list and a str object, except that it also has such useful
    attributes like `optional` and `variable`."""

    def __init__(self, text=None, optional=False, runs=False, variable=False):
        """
        Instance a `Block` object.

        :param text: an object containing symbols to be converted into `Char`
        objects. Accepted types are `Paragraph`, `Char`, `Block`, `str`. The
        styling of each character, if present, is retained. If not given,
        an empty `Block` object will be constructed.
        :param optional: `bool`. A flag to signal whether the `Block` should
        be optional or obligatory.
        :param runs: signals that `text` is a Paragraph. Should be
        refactored into `isinstance(text, Paragraph).
        :param variable: `bool`. A flag to signal whether the `Block` should
        be variable or constant.
        """

        super().__init__()
        self.chars = []
        self.optional = optional
        self.variable = variable

        # Since empty Blocks are also allowed, this condition is present
        # here. Depending on the type of `text` that is given, `self.chars`
        # is constructed differently. `runs` signals that `text` is a
        # Paragraph object and each run should be extracted first to
        # specify the styling of each `Char`.
        if text:
            if runs:
                self._paragraph = text
                self._runs = self._paragraph.runs
                for run in self._runs:
                    for char in run.text:
                        self.chars.append(Char(char, run))
                # Extract each char within the Block into a Char object and
                # save its formatting.

            elif isinstance(text, str):
                for char in text:
                    self.chars.append(Char(char))
                # Extract each char within the text and make an unformatted
                # Char object from it.

            elif isinstance(text, Char):
                self.chars.append(text)
                # Add the char a one Char object Block

            elif isinstance(text, Block):
                self.chars.extend(text.chars)
                # Reuse the chars of the fed Block as this new Block's chars.

            else:
                for char in text:
                    self.chars.append(char)
                # Make a Block out of list of Char objects

    def index(self, value, start=0, end=None):
        """Override `.index()` method from `list` and `str` types.

        :param value: `Block`, `Char` or `str`.
        :param start: index to start searching the value from.
        :param end: index at which searching concludes.

        :return: the position of the first occurrence of `value` from the
        left. The search is formatting-insensitive.
        """
        if not end:
            end = len(self.chars)
        if isinstance(value, str):
            return "".join([char() for char in self.chars]).index(
                value, start, end)
        if isinstance(value, Block):
            return self().index(value(), start, end)
        return self.chars.index(value, start, end)

    def __getitem__(self, item):
        """Override subscription from `list` and `str` (slices and indexing)

        :param item: `int` or `Slice` object.
        :return: `Char` object if `item` is int. If `item` is `Slice`
        object, return a sliced `Block`."""
        if not isinstance(item, int):
            return Block(self.chars[item])
        return self.chars[item]

    def append(self, value):
        """Append either a `Block`, `Char or `str` objects"""
        if isinstance(value, Block):
            self.chars.extend(value.chars)
            return
        if isinstance(value, str):
            for char in value:
                self.chars.append(Char(char))
            return
        self.chars.append(value)

    def count(self, value):
        """Count the number of `Block`, `Char` or `str` occurrences."""
        if isinstance(value, str):
            return "".join([char() for char in self.chars]).count(value)
        if isinstance(value, Block):
            return "".join([char() for char in self.chars]).count(value())
        return self.chars.count(value)

    def reverse(self):
        """Reverse the order of `Chars` in `self.chars`"""
        self.chars.reverse()

    def pop(self):
        """Pop the last element of the `Block`"""
        char = self.chars.pop()
        return Block(char)

    def split(self, delimiter):
        """Split the `Block` into a list of Blocks using a `Block` delimiter.
        First split the raw string data with a string delimiter. Then
        correspond each resulting slice to a `Block` slice and append that
        to a list."""
        split_list = self().split(delimiter())
        i = 0
        j = 0
        k = 0
        _chars = []
        texts = []
        while i < len(self.chars):
            if self.chars[i]() == split_list[j][k]:
                _chars.append(self.chars[i])
                k += 1
            if k == len(split_list[j]):
                j += 1
                texts.append(Block(_chars))
                _chars = []
                k = 0
            i += 1
        return texts

    def lstrip(self):
        if self.chars:
            if ' ' == self.chars[0]():
                del self.chars[0]

    def __len__(self):
        """return the number of `Char` objects stored in `self`."""
        return len(self.chars)

    def __delitem__(self, key):
        """Delete a `Char` object with given index."""
        del self.chars[key]

    def __call__(self):
        """return the string representation of `self`"""
        return ''.join([char() for char in self.chars])

    def __add__(self, other):
        """Define concatenation when `self` is the first element"""
        if isinstance(other, str):
            result = self.chars[:]
            result.extend(Block(other).chars)
            return Block(result)
        new_chars = self.chars[:]
        new_chars.extend(other.chars)
        return Block(new_chars)

    def __radd__(self, other):
        """Define concatenation when `self` is the second element"""
        if isinstance(other, str):
            result = Block(other)
            result.chars.extend(self.chars)
            return result
        new_chars = other.chars[:]
        new_chars.extend.extend(self.chars)
        return Block(new_chars)

    def __contains__(self, item):
        """Define `in self` operator"""
        if isinstance(item, str):
            return True if self.count(item) > 0 else False
        return True if self().count(item()) > 0 else False

    def __eq__(self, other):
        if isinstance(other, Block):
            if other.chars == self.chars and \
                other.variable == self.variable and \
                other.optional == self.optional:
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Char:
    """Class to store single characters and their formatting"""

    def __init__(self, char, run=None):
        """
        Instance a `Char` object.
        :param char: string character to be stored.
        :param run: if there's any formatting, it is exctracted from a `Run`
        object
        """
        self.str = char

        self.italic = run.italic if run else None
        self.bold = run.bold if run else None
        self.underline = run.underline if run else None
        self.subscript = run.font.subscript if run else None
        self.superscript = run.font.superscript if run else None

        # This attribute comes in handy when comparing formatting style of
        # two `Char` objects and defining the style of a written `Run`.
        self.bits = [self.italic,
                     self.bold,
                     self.underline,
                     self.subscript,
                     self.superscript,
                     ]

    def __call__(self):
        """When called, return the string character"""
        return self.str

    def __eq__(self, other):
        """Allows to evaluate equality between a `Char` object and a string
        character"""
        if isinstance(other, str):
            return other == self.str
        return other is self

    def __ne__(self, other):
        """Allows to evaluate inequality between a `Char` object and a string
        character"""
        return not self.__eq__(other)