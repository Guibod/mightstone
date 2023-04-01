import bz2
import csv
import gzip
import io
import lzma
from contextlib import contextmanager
from typing import AsyncGenerator, Union


async def async_gen_to_list(async_gen: AsyncGenerator):
    result = []
    async for obj in async_gen:
        result.append(obj)

    return result


def uncompress_none(filename: str):
    with open(filename, "rb") as fd:
        return list(fd)


def uncompress_gzip(filename: str):
    with gzip.open(filename) as gzfd:
        return list(gzfd)


def uncompress_bzip2(filename: str):
    with bz2.open(filename) as bz2fd:
        return list(bz2fd)


def uncompress_lzma(filename: str):
    with lzma.open(filename) as lzmafd:
        return list(lzmafd)


@contextmanager
def open_file_or_bytesio(file: Union[str, io.BytesIO]):
    if isinstance(file, str):
        with open(file, "rb") as fd:
            yield fd
    else:
        yield file


def compress_none(filename: str):
    with open(filename, "rb") as fd:
        return fd.read()


def compress_gzip(file: Union[str, io.BytesIO]):
    buffer = io.BytesIO()
    with open_file_or_bytesio(file) as fd:
        with gzip.open(buffer, "wb") as gzfd:
            gzfd.write(fd.read())
    return buffer.getvalue()


def compress_bzip2(file: Union[str, io.BytesIO]):
    buffer = io.BytesIO()
    with open_file_or_bytesio(file) as fd:
        with bz2.open(buffer, "wb") as bz2fd:
            bz2fd.write(fd.read())
    return buffer.getvalue()


def compress_lzma(file: Union[str, io.BytesIO]):
    buffer = io.BytesIO()
    with open_file_or_bytesio(file) as fd:
        with lzma.open(buffer, "wb") as lzmafd:
            lzmafd.write(fd.read())
    return buffer.getvalue()


def compress(file, compression=None):
    if compression is None:
        return compress_none(file)
    elif compression == "gzip":
        return compress_gzip(file)
    elif compression == "bzip2":
        return compress_bzip2(file)
    elif compression == "lzma":
        return compress_lzma(file)
    else:
        raise Exception(
            "Compression {compression} not supported".format(compression=compression)
        )


def uncompress(file, compression=None):
    if compression is None:
        return uncompress_none(file)
    elif compression == "gzip":
        return uncompress_gzip(file)
    elif compression == "bzip2":
        return uncompress_bzip2(file)
    elif compression == "lzma":
        return uncompress_lzma(file)
    else:
        raise Exception(
            "Compression {compression} not supported".format(compression=compression)
        )


def get_raw_rows(filename: str, compression=None):
    return list(
        csv.reader([line.decode("utf-8") for line in uncompress(filename, compression)])
    )


def get_raw_lines(filename: str, compression=None):
    return uncompress(filename, compression)
