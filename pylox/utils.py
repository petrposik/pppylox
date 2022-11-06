from collections import deque


class PeekableIO:
    def __init__(self, stream, lookahead=1):
        self.stream = stream
        self.position = 0
        self.lookahead = lookahead
        self._cache = self.init_cache()

    def init_cache(self):
        d = deque()
        for _ in range(self.lookahead):
            d.append(self.stream.read(1))
        return d

    def consume(self):
        """Consume and return next char"""
        self._cache.append(self.stream.read(1))
        self.position += 1
        return self._cache.popleft()

    def peek(self, index=0):
        """Return (one of) the next item(s) without consuming. Return "" if there are no more items."""
        if index >= self.lookahead:
            raise IndexError(
                f"Attempted to peek at index {index}. Maximum index you can peek at is {self.lookahead-1}."
            )
        return self._cache[index]

    def __iter__(self):
        return self

    def __bool__(self):
        return self.peek() != ""

    def tell(self):
        return self.position

    @property
    def exhausted(self):
        return self.peek() == ""

    def __next__(self):
        if self.exhausted:
            raise StopIteration
        return self.consume()

    def consume_if(self, predicate):
        """Advance if the returned char fulfills the ``predicate``.

        Otherwise return None.
        """
        char = self.peek()
        if char and predicate(char):
            return self.consume()
        return None

    def accept(self, allowed):
        """Return next char if it is one of the allowed ones; return None otherwise."""
        char = self.peek()
        if char and char in allowed:
            return self.consume()
        return None

    def expect(self, allowed):
        """Return next char if it is one of the allowed ones; raise ValueError otherwise."""
        char = self.peek(None)
        if char and char in allowed:
            return self.consume()
        raise ValueError("Expected one of '{allowed}' characters, but found '{char}'.")


class Peekable:
    def __init__(self, seq, lookahead=1):
        self.seq = seq
        self.position = 0
        self.lookahead = lookahead
        self._cache = self.init_cache()

    def init_cache(self):
        d = deque()
        for _ in range(self.lookahead):
            d.append(self.read_from_seq())
        return d

    def read_from_seq(self):
        try:
            item = next(self.seq)
        except StopIteration:
            item = None
        return item

    def consume(self):
        """Consume and return next char"""
        self._cache.append(self.read_from_seq())
        self.position += 1
        return self._cache.popleft()

    def peek(self, index=0):
        """Return (one of) the next item(s) without consuming. Return "" if there are no more items."""
        if index >= self.lookahead:
            raise IndexError(
                f"Attempted to peek at index {index}. Maximum index you can peek at is {self.lookahead-1}."
            )
        return self._cache[index]

    def __iter__(self):
        return self

    def __bool__(self):
        return self.peek() is not None

    def tell(self):
        return self.position

    @property
    def exhausted(self):
        return self.peek() is None

    def __next__(self):
        if self.exhausted:
            raise StopIteration
        return self.consume()

    def consume_if(self, predicate):
        """Consume if the returned char fulfills the ``predicate``.

        Otherwise return None.
        """
        item = self.peek()
        if item and predicate(item):
            return self.consume()
        return None
