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

# 複数の読みを持つ漢字のリスト
MULTI_READ_KANJI_LIST = [
    '風','何','観','方','出','時','上','下','君','手','嫌','表',
    '対','色','人','前','後','角','金','頭','筆','水','間','棚',
    # 以下、Wikipedia「同形異音語」からミスりそうな漢字を抜粋 (ただしこれらは NN 使わない限り完璧な判定は無理な気がする…)
    # Sudachi の方が不正確な '汚','通','臭','辛' は除外した
    # ref: https://ja.wikipedia.org/wiki/%E5%90%8C%E5%BD%A2%E7%95%B0%E9%9F%B3%E8%AA%9E
    '床','入','来','塗','怒','包','被','開','弾','捻','潜','支','抱','行','降','種','訳','糞',
    # 以下、Wikipedia「同形異音語」記事内「読み方が3つ以上ある同形異音語」より
    '空','性','体','等','生','止','堪','捩',
    # 以下、独自に追加
    '家','縁','労','中','高','低','気','要','退','面','色','主','術','直','片','緒','小','大',
    # 他にも日付（月・火・水・木・金・土・日）も入るが、当面は入れない (金を除く)
]  # fmt: skip

def preserve_noun_accent(
    input_njd: list[NjdObject], predicted_njd: list[NjdObject]
) -> list[NjdObject]:
    return_njd = []
    for f_input, f_pred in zip(input_njd, predicted_njd):
        if f_pred["pos"] == "名詞" and f_pred["string"] not in MULTI_READ_KANJI_LIST:
            f_pred["acc"] = f_input["acc"]
        return_njd.append(f_pred)

    return return_njd
