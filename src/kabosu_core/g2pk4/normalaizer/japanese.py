# MIT License

# Copyright (c) 2023 Sleeping KDR

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

# code from kdrkdrkdr/g2pk3

from kabosu_core.g2pk4.korean import join_jamos
import re
import re2
import kabosu_core

patt_repl = [
    # 외래어 
    ('ヴァ', 'ㅂㅏ'),
    ('ヴィ', 'ㅂㅣ'),
    ('ヴェ', 'ㅂㅔ'),
    ('ヴォ', 'ㅂㅗ'),
    ('ヴ', 'ㅂㅜ'),
    ('ツァ', 'ㅊㅏ'),
    ('ツィ', 'ㅊㅣ'),
    ('ツェ', 'ㅊㅔ'),
    ('ツォ', 'ㅊㅗ'),


    # 가타카나 50음도
    ('ア',    'ㅇㅏ'),
    ('イ',    'ㅇㅣ'),
    ('ウ',    'ㅇㅜ'),
    ('エ',    'ㅇㅔ'),
    ('オ',    'ㅇㅗ'),

    ('カ',       'ㅋㅏ'),
    ('キ',       'ㅋㅣ'),
    ('ク',       'ㅋㅜ'),
    ('ケ',       'ㅋㅔ'),
    ('コ',       'ㅋㅗ'),

    ('ガ',       'ㄱㅏ'),
    ('ギ',       'ㄱㅣ'),
    ('グ',       'ㄱㅜ'),
    ('ゲ',       'ㄱㅔ'),
    ('ゴ',       'ㄱㅗ'),

    ('サ',       'ㅅㅏ'),
    ('シ',       'ㅅㅣ'),
    ('ス',       'ㅅㅡ'),
    ('セ',       'ㅅㅔ'),
    ('ソ',       'ㅅㅗ'),

    ('ザ',       'ㅈㅏ'),
    ('ジ',       'ㅈㅣ'),
    ('ズ',       'ㅈㅡ'),
    ('ゼ',       'ㅈㅔ'),
    ('ゾ',       'ㅈㅗ'),

    ('タ',       'ㅌㅏ'),
    ('チ',       'ㅊㅣ'),
    ('ツ',       'ㅊㅡ'),
    ('テ',       'ㅌㅔ'),
    ('ト',       'ㅌㅗ'),

    ('ダ',       'ㄷㅏ'),
    ('ヂ',       'ㅈㅣ'),
    ('ヅ',       'ㅈㅡ'),
    ('デ',       'ㄷㅔ'),
    ('ド',       'ㄷㅗ'),

    ('ナ',       'ㄴㅏ'),
    ('ニ',       'ㄴㅣ'),
    ('ヌ',       'ㄴㅜ'),
    ('ネ',       'ㄴㅔ'),
    ('ノ',       'ㄴㅗ'),

    ('ハ',       'ㅎㅏ'),
    ('ヒ',       'ㅎㅣ'),
    ('フ',       'ㅎㅜ'),
    ('ヘ',       'ㅎㅔ'),
    ('ホ',       'ㅎㅗ'),

    ('バ',       'ㅂㅏ'),
    ('ビ',       'ㅂㅣ'),
    ('ブ',       'ㅂㅜ'),
    ('ベ',       'ㅂㅔ'),
    ('ボ',       'ㅂㅗ'),

    ('パ',       'ㅍㅏ'),
    ('ピ',       'ㅍㅣ'),
    ('プ',       'ㅍㅜ'),
    ('ペ',       'ㅍㅔ'),
    ('ポ',       'ㅍㅗ'),

    ('マ',       'ㅁㅏ'),
    ('ミ',       'ㅁㅣ'),
    ('ム',       'ㅁㅜ'),
    ('メ',       'ㅁㅔ'),
    ('モ',       'ㅁㅗ'),

    ('ヤ',       'ㅇㅑ'),
    ('ユ',       'ㅇㅠ'),
    ('ヨ',       'ㅇㅛ'),

    ('ラ',       'ㄹㅏ'),
    ('リ',       'ㄹㅣ'),
    ('ル',       'ㄹㅜ'),
    ('レ',       'ㄹㅔ'),
    ('ロ',       'ㄹㅗ'),

    ('ワ',       'ㅇㅘ'),
    ('ヲ',       'ㅇㅗ'),

    ('ン',       'N'),
    ('ッ',       'Q'),

    (r'([ㄷㅌ])ㅔィ',       r'\1ㅣ'),
    (r'([ㄷㅌ])ㅗゥ',       r'\1ㅜ'),

    # 요음처리 (ャ, ュ, ョ)
    ('ㅣャ',       'ㅑ'),
    ('ㅣュ',       'ㅠ'),
    ('ㅣョ',       'ㅛ'),
    ('ャ',       'ㅇㅑ'),
    ('ュ',       'ㅇㅠ'),
    ('ョ',       'ㅇㅛ'),

    # 작은 아이우에오
    (r'([ㅜㅗ])ァ', 'ㅘ'),
    (r'([ㅜ])ィ', 'ㅟ'),
    (r'([ㅔ])ィ', 'ㅣ'),
    (r'([ㅗ])ゥ', 'ㅗ'),
    (r'([ㅣ])ェ', 'ㅖ'),
    (r'([ㅜ])ェ', 'ㅞ'),
    (r'([ㅜ])ォ', 'ㅝ'),

    # 장음처리
    (r'([ㅑㅏ])ァ', r'\1ㅇㅏ'),
    (r'([ㅣ])ィ', r'\1ㅇㅣ'),
    (r'([ㅠㅜ])ゥ', r'\1ㅇㅜ'),
    (r'([ㅡ])ゥ', r'\1ㅇㅡ'),
    (r'([ㅖㅔ])ェ', r'\1ㅇㅔ'),
    (r'([ㅛㅗ])ォ', r'\1ㅇㅗ'),
    ('ァ',      'ㅇㅏ'),
    ('ィ',      'ㅇㅣ'),
    ('ゥ',      'ㅇㅜ'),
    ('ェ',      'ㅇㅔ'),
    ('ォ',      'ㅇㅗ'),
    (r'([ㅑㅏ])ー', r'\1ㅇㅏ'),
    (r'([ㅣ])ー', r'\1ㅇㅣ'),
    (r'([ㅠㅜ])ー', r'\1ㅇㅜ'),
    (r'([ㅡ])ー', r'\1ㅇㅡ'),
    (r'([ㅖㅔ])ー', r'\1ㅇㅔ'),
    (r'([ㅛㅗ])ー', r'\1ㅇㅗ'),
    ('ー', ''),

    # 받침 
    (r'([ㅏ-ㅣ])Q([ㄱㄷㅅ])', r'\1\2\2'),
    (r'([ㅏ-ㅣ])Q([ㅊ])', r'\1ㄷ\2'),
    (r'([ㅏ-ㅣ])Q([ㅍ])', r'\1ㅂ\2'),
    (r'([ㅏ-ㅣ])Q([ㄴㄹㅁㅂㅇㅈㅋㅌㅎ]|$)', r'\1ㅅ\2'),
    (r'(Q+)', '읏'),
    (r'([ㅏ-ㅣ])N([ㅁㅂㅍ])', r'\1ㅁ\2'),
    (r'([ㅏ-ㅣ])N([ㄱㅇㅋㅎ])', r'\1ㅇ\2'),
    (r'([ㅏ-ㅣ])N([ㄴㄷㄹㅅㅈㅊㅌ]|$)', r'\1ㄴ\2'),
    (r'(N+)', lambda match: '으'*(len(match.group())-1) + '응'),
]

def convert_j2k(string, for_ko=False):
    word = kabosu_core.g2p(string, kana=True,) #for_ko=for_ko)
    for pattern, repl in patt_repl:
        word = re.sub(pattern, repl, word)
    word = join_jamos(word) \
        .replace('。', '.') \
        .replace('？', '?') \
        .replace('！', '!') \
        .replace('、', ',') \
        .replace('・', ' ')
    return word


def convert_jpn(string):
    return re2.sub("[０-９ぁ-ゔァ-ヴ一-龥ー。？！、・']+", lambda x: convert_j2k(x.group(0), True), string)
