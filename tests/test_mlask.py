# -*- coding: utf-8 -*-


# The BSD 3-Clause License

# Copyright (c) 2017, Yukino Ikegami
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

#   * Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#   * Neither the name of the ML-Ask system nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import unicode_literals
from kabosu_core.language.njd.ja.lib.mlask import MLAsk

mla = MLAsk()

def test__read_emodic():
    assert ('！' in mla.emodic['emotem']['exclamation']) == True
    assert ('嫌い' in mla.emodic['emotion']['iya']) == True

def test_analyze():
    result = mla.analyze('彼は嫌いではない！(;´Д`)')
    assert result['text'] == '彼は嫌いではない！(;´Д`)'
    result = mla.analyze('')
    assert result == {'text': '', 'emotion': None}

def test__normalize():
    assert mla._normalize('!') == '！'
    assert mla._normalize('?') == '？'

def test__lexical_analysis():
    assert mla._lexical_analysis('すごい') == {'all': 'すごい', 'interjections': [], 'no_emotem': 'すごい', 'lemma_words': ['すごい']}

def test__find_emoticon():
    assert mla._find_emoticon('(;´Д`)') == ['(;´Д`)']
    assert mla._find_emoticon('顔文字なし') == []

def test__find_emotem():
    assert mla._find_emotem({'no_emotem': '(;´Д`)', 'interjections': '！'}, []) == {'emotikony': ['´Д`', 'Д`', '´Д'], 'interjections': ['！']}

def test__find_emotion():
    lemmas = {'all': '嫌い', 'lemma_words': ['嫌い']}
    assert mla._find_emotion(lemmas) == {'iya': ['嫌い']}

    lemmas_with_interjections = {'all': 'え！嫌い', 'interjections': ['え'], 'lemma_words': ['え','！', '嫌い']}
    assert mla._find_emotion(lemmas_with_interjections) == {'iya': ['嫌い']}
    
    empty_lemmas = {'all': [], 'interjections': [], 'no_emotem': [], 'lemma_words': []}
    assert mla._find_emotion(empty_lemmas) == None
    
    lemmas = {'all': '気持ちがよい', 'lemma_words': ['気持ち', 'が', 'よい']}
    assert mla._find_emotion(lemmas) == {'yorokobi': ['気持ちがよい']}

def test__estimate_sentiment_orientation():
    assert mla._estimate_sentiment_orientation({'iya': ['嫌い', '嫌']}) == 'NEGATIVE'
    assert mla._estimate_sentiment_orientation({'yorokobi': ['嫌い*CVS']}) == 'POSITIVE'
    assert mla._estimate_sentiment_orientation({'yorokobi': ['嫌い*CVS'], 'iya': ['嫌い']}) == 'NEUTRAL'
    assert mla._estimate_sentiment_orientation({'iya': ['嫌い', '嫌'], 'aware': ['悲しい'], 'yorokobi': ['嬉しい']}) == 'mostly_NEGATIVE'
                                                      

def test__estimate_activation():
    assert mla._estimate_activation({'kowa': ['怖い']}) == 'ACTIVE'
    assert mla._estimate_activation({'aware': ['悲しい']}) == 'PASSIVE'
    assert mla._estimate_activation({'iya': ['嫌い', '嫌']}) == 'NEUTRAL'
    assert mla._estimate_activation({'kowa': ['怖い'], 'yasu': ['安らぐ'], 'aware': ['悲しい']}) == 'mostly_PASSIVE'
                                           

def test__get_representative_emotion():
    assert mla._get_representative_emotion({'iya': ['嫌い', '嫌']}) == ('iya', ['嫌い', '嫌'])
