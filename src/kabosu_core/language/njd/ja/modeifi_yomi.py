#The pyopenjtalk package is licensed under the MIT "Expat" License:
#
#> Copyright (c) 2018: Ryuichi Yamamoto.
#>
#> Permission is hereby granted, free of charge, to any person obtaining
#> a copy of this software and associated documentation files (the
#> "Software"), to deal in the Software without restriction, including
#> without limitation the rights to use, copy, modify, merge, publish,
#> distribute, sublicense, and/or sell copies of the Software, and to
#> permit persons to whom the Software is furnished to do so, subject to
#> the following conditions:
#>
#> The above copyright notice and this permission notice shall be
#> included in all copies or substantial portions of the Software.
#>
#> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#> EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#> MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#> IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
#> CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#> TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#> SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#/bAmFru).
from kabosu_core.language.types import NjdObject
from kabosu_core.language.njd.ja.nani_predict import predict
from sudachipy import dictionary, tokenizer

def modify_kanji_yomi(
    text: str, pyopen_njd: list[NjdObject], multi_read_kanji_list: list[str]
) -> list[NjdObject]:
    sudachi_yomi = sudachi_analyze(text, multi_read_kanji_list)
    return_njd = []
    pre_dict = None

    for dict in reversed(pyopen_njd):
        if dict["orig"] in multi_read_kanji_list:
            try:
                correct_yomi = sudachi_yomi.pop()
            except IndexError:
                return pyopen_njd
            if correct_yomi[0] != dict["orig"]:
                return pyopen_njd
            elif dict["orig"] == "何":
                is_read_nan = predict([pre_dict])
                if is_read_nan == 1:
                    dict["pron"] = "ナン"
                    dict["read"] = "ナン"
                else:
                    dict["pron"] = "ナニ"
                    dict["read"] = "ナニ"
                return_njd.append(dict)

            else:
                if correct_yomi[0] == "方" and correct_yomi[1] == "ホウ":
                    correct_yomi[1] = "ホオ"
                dict["pron"] = correct_yomi[1]
                dict["read"] = correct_yomi[1]
                return_njd.append(dict)
        else:
            return_njd.append(dict)
        pre_dict = dict

    return_njd.reverse()
    return return_njd


def sudachi_analyze(text: str, multi_read_kanji_list: list[str]) -> list[list[str]]:
    """
    複数の読み方をする漢字の読みを sudachi で形態素解析した結果をリストで返す
    例: 風がこんな風に吹く → [('風', 'カゼ'), ('風', 'フウ')]

    Args:
        text (str): 読み対象となるテキスト
        multi_read_kanji_list (list[str]): 複数の読み方をする漢字のリスト(ex : 何、風、方)

    Returns:
        yomi_list (list[list[str]]): 漢字とその読み方のリスト
    """

    text = text.replace("ー", "")
    tokenizer_obj = dictionary.Dictionary().create()
    mode = tokenizer.Tokenizer.SplitMode.C
    m_list = tokenizer_obj.tokenize(text, mode)
    yomi_list = [
        [m.surface(), m.reading_form()] for m in m_list if m.surface() in multi_read_kanji_list
    ]
    return yomi_list