# MIT License

# Copyright (c) 2022 Sam Passaglia

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



import pytest
from kabosu_core.language.ja.g2p.yomikata.dictionary import Dictionary
from kabosu_core.language.ja.g2p.yomikata.dbert import dBert

def test_yomikata_reader_furigana_test():
    text = 'そして、畳の表は、すでに幾年前に換えられたのか分らなかった。'
    reader = dBert()
    output = reader.furigana(text)
    assert output == "そして、畳の{表/おもて}は、すでに幾年前に換えられたのか分らなかった。"
    print(output)

def test_yomikata_dictreader_furigana_test():
    text = 'そして、畳の表は、すでに幾年前に換えられたのか分らなかった。'
    dictreader = Dictionary(tagger="juman")
    output = dictreader.furigana(text)
    assert output == "そして、{畳/たたみ}の{表/ひょー}は、すでに{幾/いく}{年/ねん}{前/まえ}に{換/か}えられたのか{分/わか}らなかった。"
    print(output)
