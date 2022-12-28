import os
import unittest
from __init__ import nirlibs


class TestRemove(unittest.IsolatedAsyncioTestCase):
    async def test_gc(self):
        await nirlibs.database.dump_old(0)
        self.assertEqual(os.listdir(nirlibs.database.nar_dir), [])


if __name__ == '__main__':
    unittest.main()
