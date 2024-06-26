import os
from tempfile import NamedTemporaryFile

import aiofiles
import pytest

from mightstone.ass import compressor

from .test_utils import get_raw_lines


@pytest.mark.parametrize(
    "compression",
    [
        None,
        "gzip",
        "bzip2",
        "lzma",
    ],
)
@pytest.mark.asyncio(scope="session")
async def test_open_write(compression: str):
    baby_name_filename = os.path.join(
        os.path.dirname(__file__), "data", "baby_names.csv"
    )
    with NamedTemporaryFile() as tmpfd:
        async with aiofiles.open(tmpfd.name, "wb") as rfd:
            async with aiofiles.open(baby_name_filename, "rb") as cfd:
                async with compressor.open(
                    rfd, mode="wb", compression=compression
                ) as fd:
                    await fd.write(await cfd.read())
                assert get_raw_lines(baby_name_filename) == get_raw_lines(
                    tmpfd.name, compression
                )


@pytest.mark.parametrize(
    "compression",
    [
        None,
        "gzip",
        "bzip2",
        "lzma",
    ],
)
@pytest.mark.asyncio(scope="session")
async def test_open_read_with_filename(compression: str):
    baby_name_filename = os.path.join(
        os.path.dirname(__file__), "data", "baby_names.csv"
    )
    with NamedTemporaryFile() as tmpfd:
        async with aiofiles.open(baby_name_filename, "rb") as cfd:
            async with compressor.open(
                tmpfd.name, mode="wb", compression=compression
            ) as fd:
                await fd.write(await cfd.read())
            assert get_raw_lines(baby_name_filename) == get_raw_lines(
                tmpfd.name, compression
            )
