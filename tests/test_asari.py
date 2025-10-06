# MIT License

# Copyright (c) 2019 Hiroki Nakayama

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import unittest
from pprint import pprint

from kabosu_core.language.njd.ja.lib.asari.api import Sonar


class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = "広告多すぎる♡"

    def test_ping(self):
        sonar = Sonar()
        res = sonar.ping(self.text)
        pprint(res)
        self.assertIn("text", res)
        self.assertIn("top_class", res)
        self.assertIn("classes", res)
        self.assertIsInstance(res["text"], str)
        self.assertIsInstance(res["top_class"], str)
        self.assertIsInstance(res["classes"], list)
        for d in res["classes"]:
            self.assertIn("class_name", d)
            self.assertIn("confidence", d)
            self.assertIsInstance(d["class_name"], str)
            self.assertIsInstance(d["confidence"], float)
