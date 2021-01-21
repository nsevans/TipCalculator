import unittest

import datetime

from common import utils

class TestUtils(unittest.TestCase):

    def test_is_allowed_files(self):
        """
        
        """
        file_names = ["test.pdf", "test.exe", "test.pdx"]

        result = [utils.is_allowed_file(f) for f in file_names] 
        self.assertEqual(result, [True, False, False])

    def test_format_time(self):
        """

        """
        time = datetime.datetime(2014, 3, 22, 21, 46, 38, 420690)
        result = utils.formatTime(time)
        self.assertEqual(result, "21:46:38.420690")

    def test_format_date(self):
        """
        
        """
        time = datetime.datetime(2014, 3, 22, 21, 46, 38, 420690)
        result = utils.formatDate(time)
        self.assertEqual(result, "2014-03-22")



if __name__ == "__main__":
    unittest.main()