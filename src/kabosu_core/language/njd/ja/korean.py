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


from kabosu_core.language.njd.ko import G2p




#単語の最初は静音化するとgeminiくんが言ってた
def convert_k2j(word: str, first_jamo:bool = False):

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

    #ここから逆になっているわよ！

    if first_jamo:

        for repl, pattern in SEION_LIST:
            word = word.replace(pattern, repl)

    else:

        for repl, pattern  in DAKUON_LIST:
            word = word.replace(pattern, repl)

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
    
    out_text_list = []
    for word_list in hcj_list:
        out_word = ""
        for i in range(len(word_list)):
            
            if i == 0:
                first_jamo = True
            else:
                first_jamo = False

            hcj = word_list[i]
            kana = convert_k2j(hcj, first_jamo)
            out_word += kana 

        out_text_list.append(out_word)

    out_text = "、".join(out_text_list)#読点で区切って読みやすく
    return out_text