import unittest
from __init__ import dl  # I HATE THIS TRICK


class TestDownload(unittest.IsolatedAsyncioTestCase):
    async def test_nixpkgs(self):
        for x in await dl.get_lastest_packages("nixpkgs-unstable"):
            assert len(x) == 32

    async def test_dl(self):
        await dl.get_nix_binary(
            (await dl.get_lastest_packages("nixpkgs-unstable"))[114:514]
        )


if __name__ == '__main__':
    unittest.main()
