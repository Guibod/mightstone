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
@pytest.mark.asyncio
async def test_writer(compression: str):
    baby_name_filename = os.path.join(
        os.path.dirname(__file__), "data", "baby_names.csv"
    )
    with NamedTemporaryFile(mode="wb", delete=False) as tmpfd:
        async with aiofiles.open(baby_name_filename, "rb") as rfd:
            async with aiofiles.open(tmpfd.name, "wb") as owfd:
                async with compressor.open(
                    owfd, mode="wb", compression=compression
                ) as wfd:
                    async for line in rfd:  # type: ignore
                        await wfd.write(line)
        assert get_raw_lines(baby_name_filename) == get_raw_lines(
            tmpfd.name, compression
        )
