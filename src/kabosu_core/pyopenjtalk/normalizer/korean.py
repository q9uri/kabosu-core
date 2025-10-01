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


from kabosu_core.g2pk4.g2pk4 import G2p

JP2KO_LIST = [
    
    # gemini君（ちゃん？）にコメントを書いてもらったもの
    ('ワ',       'ㅇㅘ'),# ㅘ	ㅗ+ㅏ	wa（ワ）	わ	wa	日本語の「わ」に最も近い。
    ('ウェ',       'ㅇㅙ'),# ㅙ	ㅗ+ㅐ	wɛ（ウェ）	うぇ	wae	「オ」より「ウ」の要素が強いため「うぇ」と表記されることが多い。
    ('ウェ',       'ㅇㅚ'),# ㅚ	ㅗ+ㅣ	we（ウェ）	うぇ	oe	発音は「ウェ」に近いが、まれに「おえ」とも。日本語TTSでは「うぇ」が簡潔。
    ('ウォ',       'ㅇㅝ'),# ㅝ	ㅜ+ㅓ	wʌ（ウォ）	うぉ	wo	「ウ」から始まる「オ」の音。「を」ではなく「うぉ」が音素的に正確。
    ('ウェ',       'ㅇㅞ'),# ㅞ	ㅜ+ㅔ	we（ウェ）	うぇ	we	
    ('ウィ',       'ㅇㅟ'),# ㅟ	ㅜ+ㅣ	wi（ウィ）	うぃ	wi	
    ('ウィ',       'ㅇㅢ'),# ㅢ	ㅡ+ㅣ	ɯi（ウィ/イ）	うぃ	ui
    ('ヤ',       'ㅇㅑ'),# ㅑ	ㅣ+ㅏ	ja（ヤ）	や
    ('イェ',       'ㅇㅒ'),# ㅒ	ㅣ+ㅐ	jɛ（イェ）	いぇ
    ('ヨ',       'ㅇㅕ'),# ㅕ	ㅣ+ㅓ	jʌ（ヨ）	よ
    ('イェ',       'ㅇㅖ'),# ㅖ	ㅣ+ㅔ	je（イェ）	いえ
    ('ヨ',       'ㅇㅛ'),# ㅛ	ㅣ+ㅗ	jo（ヨ）	よ
    ('ユ',       'ㅇㅠ'),# ㅠ	ㅣ+ㅜ	ju（ユ）	ゆ

    
    
    

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


    ('ヲ',       'ㅇㅗ'),


    # 요음처리 (ャ, ュ, ョ)

    #(r'([ㄷㅌ])ㅔィ',       r'\1ㅣ'),
    #(r'([ㄷㅌ])ㅗゥ',       r'\1ㅜ'),
    
    ('ァ',      'ㅇㅏ'),
    ('ィ',      'ㅇㅣ'),
    ('ゥ',      'ㅇㅜ'),
    ('ェ',      'ㅇㅔ'),
    ('ォ',      'ㅇㅗ'),
    

    # 받침 
    
    # (r'([ㅏ-ㅣ])Q([ㄱㄷㅅ])', r'\1\2\2'),
    # (r'([ㅏ-ㅣ])Q([ㅊ])', r'\1ㄷ\2'),
    # (r'([ㅏ-ㅣ])Q([ㅍ])', r'\1ㅂ\2'),
    # (r'([ㅏ-ㅣ])Q([ㄴㄹㅁㅂㅇㅈㅋㅌㅎ]|$)', r'\1ㅅ\2'),
    # (r'(Q+)', '읏'),
    # (r'([ㅏ-ㅣ])N([ㅁㅂㅍ])', r'\1ㅁ\2'),
    # (r'([ㅏ-ㅣ])N([ㄱㅇㅋㅎ])', r'\1ㅇ\2'),
    # (r'([ㅏ-ㅣ])N([ㄴㄷㄹㅅㅈㅊㅌ]|$)', r'\1ㄴ\2'),
    # (r'(N+)', lambda match: '으'*(len(match.group())-1) + '응'),
    ('ァ', 'ㅘ'),
    ('ィ', 'ㅟ'),
    ('ィ', 'ㅣ'),
    ('ゥ', 'ㅗ'),
    ('ェ', 'ㅖ'),
    ('ェ', 'ㅞ'),
    ('ォ', 'ㅝ'),

    ('ャ',       'ㅑ'),
    ('ュ',       'ㅠ'),
    ('ョ',       'ㅛ'),

    ('ゥ',       r'ㅜ'),
    #added
    ("ン", "ㄴ"),
    ("ン", "ㅇ"),
    ("ル", "ㄹ"),
    ("ッ", "ㅅ"),
    ("ッ", "ㅆ"),
    ("ッ", "ㅈ"),
    ("ッ", "ㅊ"),
    ("ッ", "ㅌ"),
    ("ッ", "ㅎ"),
]
REPLACE_MIDDLE_GOUSEI_BOIN = [
    ('ㅘ', 'ㅏ'),
    ('ㅙ', 'ㅐ'),
    ('ㅚ', 'ㅣ'),
    ('ㅝ', 'ㅓ'),
    ('ㅞ', 'ㅔ'),
    ('ㅟ', 'ㅣ'),
    ('ㅢ', 'ㅣ'),
    ('ㅑ', 'ㅏ'),
    ('ㅒ', 'ㅐ'),
    ('ㅕ', 'ㅓ'),
    ('ㅖ', 'ㅔ'),
    ('ㅛ', 'ㅗ'),
    ('ㅠ', 'ㅜ'),


]

REPLACE_BOIN =[
    ("ㅑ", "ㅏ"),   #あ
    ("ㅠ", "ㅜ"),   #う
    ("ㅡ", "ㅜ"),   #う
    ("ㅖ", "ㅔ"),   #え
    ("ㅛ", "ㅗ"),   #お
    ("ㅓ", 'ㅗ')    #お
]
GOUSEI_BOIN_LIST = [
    'ㅘ',
    'ㅙ',
    'ㅚ',
    'ㅝ',
    'ㅞ',
    'ㅟ',
    'ㅢ',
    'ㅑ',
    'ㅒ',
    'ㅕ',
    'ㅖ',
    'ㅛ',
    'ㅠ'
]
def convert_k2j(word: str):

    for pattern, repl  in REPLACE_MIDDLE_GOUSEI_BOIN:
        word_num = len(word)
        if word[0] != "ㅇ": #無音母音スタートだとワヤユヨなどになるわよ

            if word_num >= 2 and word[1] in GOUSEI_BOIN_LIST:
                word_last = word[1].replace(pattern, repl)

                if word_num == 2:
                    word = word[0] + word_last
                else:
                    word = word[0] + word_last + word[2:]

    for pattern, repl in REPLACE_BOIN:
        word = word.replace(pattern, repl)

    #ここだけ逆になっているわよ！
    for repl, pattern in JP2KO_LIST:
        word = word.replace(pattern, repl)

    return word

HANGUL_COMPTIBILITY_JAMO = r"\u3131-\u318e"

def ko2ja(text:str ) -> str:
    g2p = G2p()

    hcj_list = g2p(
                text,
                descriptive = False,
                verbose = False,
                group_vowels = True,
                to_syl = True,
                to_hcj = True,
                convert_japanese = False,
                convert_english = False,
                )
    
    out_text = ""
    for word_list in hcj_list:
        for hcj in word_list:
    
            kana = convert_k2j(hcj)
            out_text += kana
    
    return out_text