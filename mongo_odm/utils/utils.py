import itertools
import logging
import multiprocessing
import os
import sys
from contextlib import contextmanager
from glob import glob
from typing import Generator, Iterable, List

from str2bool import str2bool


def files_in_dir(directory: str, extension: str = 'xml') -> List[str]:
    directory = __clean_directory_name(directory)
    return sorted(glob(f'{directory}/*.{extension}'))


def __clean_directory_name(directory: str) -> str:
    return directory[:-1] if directory.endswith('/') else directory


SPAWN: bool = str2bool(os.getenv(key='SPAWN', default='False'))


@contextmanager
def spawn_scope(spawn: bool = None):
    if spawn is None:
        spawn = SPAWN

    if spawn:
        multiprocessing.set_start_method('spawn', force=True)

    yield

    if spawn:
        if sys.platform != "win32":
            multiprocessing.set_start_method('fork', force=True)


def iter_counter(iterable: Iterable,
                 total: int = None,
                 print_step: int = 1000,
                 print_message: str = 'Working on obj',
                 logger: logging.Logger = None) -> Generator:

    total_message = f'/{__formatted(total)}' if total else ''
    if total and print_step > total:
        print_step = total

    for i, iter_chunk in enumerate(chunks(iterable, print_step), 1):
        yield from iter_chunk
        formatted_print_message = (f'{print_message}: '
                                   f'{__formatted(i * print_step)}' +
                                   total_message)
        if logger:
            logger.info(formatted_print_message)
        else:
            print(formatted_print_message)


def __formatted(number: int) -> str:
    return format(number, ",").replace(",", " ")


def chunks(iterator: Iterable, n: int) -> Generator[Iterable, None, None]:
    iterator = iter(iterator)
    if n == 1:
        yield iterator
    else:
        for first in iterator:
            rest_of_chunk = itertools.islice(iterator, 0, n - 1)
            yield itertools.chain([first], rest_of_chunk)
