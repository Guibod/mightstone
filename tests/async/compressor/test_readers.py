import os
from tempfile import NamedTemporaryFile

import pytest

from mightstone.ass import compressor

from .test_utils import async_gen_to_list, compress, get_raw_rows


@pytest.mark.parametrize(
    "compression",
    [
        None,
        "gzip",
        "bzip2",
    ],
)
@pytest.mark.asyncio(scope="session")
async def test_reader(compression: str):
    baby_name_filename = os.path.join(
        os.path.dirname(__file__), "data", "baby_names.csv"
    )
    with NamedTemporaryFile() as tmpfd:
        tmpfd.write(compress(baby_name_filename, compression))
        tmpfd.flush()
        async with compressor.open(
            tmpfd.name, mode="rb", compression=compression
        ) as fd:
            async with compressor.reader(fd) as reader:
                assert get_raw_rows(baby_name_filename) == await async_gen_to_list(
                    reader
                )
