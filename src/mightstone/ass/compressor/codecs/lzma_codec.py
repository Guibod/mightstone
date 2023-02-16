import lzma


def get_lzma_encoder():
    return lzma.LZMACompressor()


def get_lzma_decoder():
    return lzma.LZMADecompressor()
