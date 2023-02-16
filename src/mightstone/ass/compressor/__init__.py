"""
This code was extracted from the asyncstream library that is licenseless and
seems an abandoned project

see: https://github.com/chimpler/async-stream
"""
from typing import Iterable, Optional

from mightstone.ass.compressor.async_file_obj import AsyncFileObj
from mightstone.ass.compressor.async_reader import AsyncReader
from mightstone.ass.compressor.async_writer import AsyncWriter


def open(
    afd: str,
    mode=None,
    encoding=None,
    compression=None,
    *args,
    **kwargs,
):
    if encoding is None and compression is None:
        from mightstone.ass.compressor.codecs.none_codec import (
            NoneCompressor,
            NoneDecompressor,
        )

        compressor = NoneCompressor()
        decompressor = NoneDecompressor()
    elif compression == "gzip":
        from mightstone.ass.compressor.codecs.gzip_codec import (
            get_gzip_decoder,
            get_gzip_encoder,
        )

        compressor = get_gzip_encoder()
        decompressor = get_gzip_decoder()
    elif compression == "lzma":
        from mightstone.ass.compressor.codecs.lzma_codec import (
            get_lzma_decoder,
            get_lzma_encoder,
        )

        compressor = get_lzma_encoder()
        decompressor = get_lzma_decoder()
    elif compression == "bzip2":
        from mightstone.ass.compressor.codecs.bzip2_codec import (
            get_bzip2_decoder,
            get_bzip2_encoder,
        )

        compressor = get_bzip2_encoder()
        decompressor = get_bzip2_decoder()
    else:
        raise ValueError("Unsupported compression %s" % compression)

    return AsyncFileObj(afd, mode, compressor, decompressor, *args, **kwargs)


def reader(
    afd: AsyncFileObj,
    has_header: bool = True,
    columns: Optional[Iterable[str]] = None,
    column_types: Optional[Iterable[str]] = None,
):
    return AsyncReader(afd, columns, column_types, has_header)


def writer(afd: AsyncFileObj, has_header: bool = True):
    return AsyncWriter(afd, has_header=has_header)
