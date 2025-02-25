#!/usr/bin/env pypy3
"""An executable, treated like a living entity."""

import array
from pathlib import Path
from typing import List, Tuple, Union

import run
from utils import to_bytes, toggle_bit_in_byte

RunResult = Tuple[int, str, str, str]
ZoonInit = Union[str, Path, "Zoon"]


class Zoon:
    """Create a Zoon from a file, a string, or another Zoon.
    :param Path, str, or Zoon: filepath or {0,1} or another Zoon
    """

    def __init__(self, initializer: ZoonInit) -> None:
        """Instantiate a Zoon."""
        self._initializer = initializer
        self.__byteseq = array.array("B")  # array of unsigned chars
        if isinstance(initializer, Path):
            path = Path(initializer)
            assert path.is_file()
            with open(initializer, "rb") as fin:
                self.__byteseq.fromfile(fin, path.stat().st_size)
        elif isinstance(initializer, str):
            assert set(initializer) <= {"0", "1"}
            self.__byteseq.frombytes(to_bytes(initializer))
        elif isinstance(initializer, Zoon):
            self.__byteseq.extend(initializer.byteseq)
        else:
            raise TypeError(f"bad initializer type: {type(initializer)}")

    @property
    def byteseq(self) -> array.array:
        """When you really need the underlying array.
        :returns: The bytearray
        :rtype: array.array
        """
        return self.__byteseq

    @byteseq.setter
    def byteseq(self, new_list: List[int]) -> None:
        """When you really need the underlying array.
        :param list[int] new_list: The new bytearray
        """
        self.__byteseq = array.array("B", new_list)

    def __len__(self) -> int:
        """Return the length in bits.
        :returns: length in bits
        :rtype: int
        """
        return len(self.__byteseq) * 8

    def __repr__(self) -> str:
        """return something that looks just like the object."""
        return f"zoon.Zoon('{self._initializer}')"

    def write(self, file_path: Path) -> Path:
        """Write Zoon to file.
        Create a file by the current filename
        :param str path: The path to write to.
        :return: path to written filename
        """
        with open(file_path, "wb") as fout:
            self.__byteseq.tofile(fout)
        return file_path

    def mutate_and_run(
        self, position: int, dir_path: Path, cmd_args: str = "", timeout: int = 1
    ) -> RunResult:
        """Mutate, then run.  Just what it sounds like."""
        mutant = self.mutate(position)
        file_path = dir_path / str(position)
        return mutant.run(file_path, cmd_args, timeout)

    def mutate(self, position: int) -> "Zoon":
        """Point-mutate Zoon bytes at the given position.
        :param int position: the position of the point mutation
        :return: mutant
        :rtype: zoon.Zoon
        assert position >= 0
        return new array with bitflip at position
        """
        # TODO: exception if position > len(Zoon)

        byte, bit = divmod(position, 8)
        mutant = Zoon(self)
        mutant.byteseq[byte] = toggle_bit_in_byte(7 - bit, mutant.byteseq[byte])
        return mutant

    def run(self, file_path: Path, cmd_args: str = "", timeout: int = 1) -> RunResult:
        """Run the Zoon with the given args for timeout seconds, max.
        :param pathlib.Path filepath: where to write and run the Zoon
        :param str cmd_args: what to pass the Zoon as args
        :param int timeout: timeout in seconds
        :raises: Exception if timeout
        :return: the exit status, optionally the output
        :rtype: tuple(int, str, str, str)
        """
        assert timeout > 0
        file_path = self.write(file_path)
        file_path.chmod(0o755)
        command = "%s %s" % (file_path, cmd_args)
        return run.run(command, timeout=timeout)

    def delete(self, start: int, stop: int) -> "Zoon":
        """Delete slice from start to stop.
        :param int start: starting byte
        :param int stop: end byte (open interval)
        :returns: mutant
        :rtype: zoon.Zoon
        """
        # TODO: range checks
        mutant = Zoon(self)
        byteseq = mutant.byteseq
        mutant.byteseq = byteseq[:start] + byteseq[stop:]
        return mutant

    # nothing below this implemented

    def __str__(self):
        """Print something more attractive."""

    def insert(self, position, insertion):
        """Return new Zoon with insertion (a Zoon).
        :param int position: position of insertion
        :param Zoon insertion: The chunk to insert
        :returns: new Zoon with insertion inserted
        :rtype: Zoon
        """

    def invert(self, chunk):
        """Invert a chunk of the Zoon.
        :param slice chunk:
        :returns: new Zoon with chunk inverted
        :rtype: Zoon

        assert isinstance(slice, Slice)
        invert the slice
        """

    def cross(self, other, position):
        """Return a new Zoon that's self[:position] + other[position:].
        :param Zoon other: The other Zoon to cross with
        :param int position: Where to cross-over
        :returns: the recombinant
        :rtype: Zoon
        """
