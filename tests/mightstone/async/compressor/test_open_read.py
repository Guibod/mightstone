import os
from tempfile import NamedTemporaryFile

import aiofiles
import pytest

from mightstone.ass import compressor

from .test_utils import async_gen_to_list, compress, get_raw_lines


@pytest.mark.parametrize(
    "compression",
    [None, "gzip", "bzip2", "lzma"],
)
@pytest.mark.asyncio
async def test_open_read(compression: str):
    baby_name_filename = os.path.join(
        os.path.dirname(__file__), "data", "baby_names.csv"
    )
    with NamedTemporaryFile() as tmpfd:
        tmpfd.write(compress(baby_name_filename, compression))
        tmpfd.flush()
        async with aiofiles.open(tmpfd.name, "rb") as cfd:
            async with compressor.open(cfd, mode="rb", compression=compression) as fd:
                assert get_raw_lines(baby_name_filename) == await async_gen_to_list(fd)


@pytest.mark.parametrize(
    "compression",
    [None, "gzip", "bzip2", "lzma"],
)
@pytest.mark.asyncio
async def test_open_read_with_filename(compression: str):
    baby_name_filename = os.path.join(
        os.path.dirname(__file__), "data", "baby_names.csv"
    )
    with NamedTemporaryFile() as tmpfd:
        tmpfd.write(compress(baby_name_filename, compression))
        tmpfd.flush()
        async with compressor.open(
            tmpfd.name, mode="rb", compression=compression
        ) as fd:
            assert get_raw_lines(baby_name_filename) == await async_gen_to_list(fd)
