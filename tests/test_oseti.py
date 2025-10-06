# -*- coding: utf-8 -*-

# MIT License

# Copyright (c) 2019 IKEGAMI Yukino

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


from kabosu_core.language.njd.ja.lib import oseti


def test_lookup_wago():
    a = oseti.Analyzer()
    actual = a._lookup_wago('うんざり', [])
    assert actual == 'うんざり'
    actual = a._lookup_wago('軽い', ['尻', 'が'])
    assert actual == '尻 が 軽い'
    actual = a._lookup_wago('どうでもいい', [])
    assert actual == ''

def test_has_arujanai():
    a = oseti.Analyzer()
    actual = a._has_arujanai('やる気あるじゃない')
    assert actual == True
    actual = a._has_arujanai('やる気ないじゃない')
    assert actual == False

def test_calc_sentiment_polarity():
    a = oseti.Analyzer()
    actual = a._calc_sentiment_polarity('最高な仕事')
    assert actual == [['最高', 1]]
    actual = a._calc_sentiment_polarity('貪欲じゃないじゃない。')
    assert actual == [['貪欲', -1]]
    actual = a._calc_sentiment_polarity('どうでもいい')
    assert actual == []
    actual = a._calc_sentiment_polarity('お金も希望もある')
    assert actual == [['お金', 1], ['希望', 1]]
    actual = a._calc_sentiment_polarity('お金とか希望なりない')
    assert actual == [['お金-NEGATION', -1], ['希望-NEGATION', -1]]
    actual = a._calc_sentiment_polarity('お金だの希望だの喜びだのない')
    assert actual == [['お金-NEGATION', -1], ['希望-NEGATION', -1], ['喜び-NEGATION', -1]]
    actual = a._calc_sentiment_polarity('お金と希望や喜びがない')
    assert actual == [['お金-NEGATION', -1], ['希望-NEGATION', -1], ['喜び-NEGATION', -1]]
    actual = a._calc_sentiment_polarity('お金があるじゃない')
    assert actual == [['お金', 1]]

def test_count_polarity():
    a = oseti.Analyzer()
    text = '遅刻したけど楽しかったし嬉しかった。すごく充実した！'
    actual = a.count_polarity(text)
    assert actual == [{'positive': 2, 'negative': 1}, {'positive': 1, 'negative': 0}]
    text = 'そこにはいつもと変わらない日常があった。'
    actual = a.count_polarity(text)
    assert actual == [{'positive': 0, 'negative': 0}]

def test_analyze():
    a = oseti.Analyzer()
    text = '遅刻したけど楽しかったし嬉しかった。すごく充実した！'
    actual = a.analyze(text)
    assert actual == [0.3333333333333333, 1.0]
    text = 'そこにはいつもと変わらない日常があった。'
    actual = a.analyze(text)
    assert actual == [0.0]

def test_analyze_detail():
    a = oseti.Analyzer()
    text = '遅刻したけど楽しかったし嬉しかった。すごく充実した！'
    actual = a.analyze_detail(text)
    assert actual == [{'positive': ['楽しい', '嬉しい'], 'negative': ['遅刻'], 'score': 0.3333333333333333},
                          {'positive': ['充実'], 'negative': [], 'score': 1.0}]
    actual = a.analyze_detail('お金も希望もない！')
    assert actual == [{'positive': [], 'negative': ['お金-NEGATION', '希望-NEGATION'], 'score': -1.0}]
    actual = a.analyze_detail('お金がないわけではない')
    assert actual == [{'positive': ['お金'], 'negative': [], 'score': 1.0}]
