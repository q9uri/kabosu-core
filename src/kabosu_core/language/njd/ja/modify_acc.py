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
from typing import Any

def merge_njd_marine_features(
    njd_features: list[NjdObject], marine_results: dict[str, Any]
) -> list[NjdObject]:
    features = []

    marine_accs = marine_results["accent_status"]
    marine_chain_flags = marine_results["accent_phrase_boundary"]

    assert len(njd_features) == len(marine_accs) == len(marine_chain_flags), (
        "Invalid sequence sizes in njd_results, marine_results"
    )

    for node_index, njd_feature in enumerate(njd_features):
        _feature = {}
        for feature_key in njd_feature.keys():
            if feature_key == "acc":
                _feature["acc"] = int(marine_accs[node_index])
            elif feature_key == "chain_flag":
                _feature[feature_key] = int(marine_chain_flags[node_index])
            else:
                _feature[feature_key] = njd_feature[feature_key]
        features.append(_feature)
    return features


def retreat_acc_nuc(njd_features: list[NjdObject]) -> list[NjdObject]:
    """
    長母音、重母音、撥音がアクセント核に来た場合にひとつ前のモーラにアクセント核がズレるルールの実装

    Args:
        njd_features (list[NjdObject]): run_frontend() の結果

    Returns:
        list[NjdObject]: 修正後の njd_features
    """

    if not njd_features:
        return njd_features

    inappropriate_for_nuclear_chars = ["ー", "ッ", "ン"]
    delete_youon = str.maketrans("", "", "ャュョァィゥェォ")
    phase_len = 0
    acc = 0
    head = njd_features[0]

    for _, njd in enumerate(njd_features):
        # アクセント境界直後の node (chain_flag 0 or -1) にアクセント核の位置の情報が入っている
        if njd["chain_flag"] in [0, -1]:
            head = njd
            acc = njd["acc"]
            phase_len = 0

        phase_len += njd["mora_size"]
        pron = njd["pron"].translate(delete_youon)
        if len(pron) == 0:
            pron = njd["pron"]

        if acc > 0:
            if acc <= njd["mora_size"]:
                try:
                    nuc_pron = pron[acc - 1]
                except IndexError:
                    nuc_pron = pron[0]
                if nuc_pron in inappropriate_for_nuclear_chars:
                    head["acc"] += -1
                acc = -1
            else:
                acc = acc - njd["mora_size"]

    return njd_features


def modify_acc_after_chaining(njd_features: list[NjdObject]) -> list[NjdObject]:
    """
    品詞「特殊・マス」は直前に接続する動詞にアクセント核がある場合、アクセント核を「ま」に移動させる法則がある
    書きます → か[きま]す, 参ります → ま[いりま]す
    書いております → [か]いております

    Args:
        njd_features (list[NjdObject]): run_frontend() の結果

    Returns:
        list[NjdObject]: 修正後の njd_features
    """

    if not njd_features:
        return njd_features

    acc = 0
    is_after_nuc = False
    phase_len = 0
    head = njd_features[0]

    for njd in njd_features:
        # アクセント境界直後の node (chain_flag 0 or -1) にアクセント核の位置の情報が入っている
        if njd["chain_flag"] in [0, -1]:
            is_after_nuc = False
            head = njd
            acc = njd["acc"]
            phase_len = 0
        # acc = 0 の場合は「特殊・マス」は存在しないと考えてよい
        if acc == 0:
            continue
        elif is_after_nuc:
            if njd["ctype"] == "特殊・マス":
                head["acc"] = phase_len + 1 if njd["cform"] != "未然形" else phase_len + 2
            elif njd["ctype"] == "特殊・ナイ":
                head["acc"] = phase_len
            elif njd["orig"] in ["れる", "られる", "すぎる", "せる", "させる"]:
                head["acc"] = phase_len + njd["acc"]
            else:
                is_after_nuc = False
                acc = 0
            phase_len += njd["mora_size"]

        else:
            phase_len += njd["mora_size"]
            if acc <= njd["mora_size"]:
                is_after_nuc = True
            else:
                acc = acc - njd["mora_size"]

    return njd_features

def modify_filler_accent(njd: list[NjdObject]) -> list[NjdObject]:
    modified_njd = []
    is_after_filler = False
    for features in njd:
        if features["pos"] == "フィラー":
            if features["acc"] > features["mora_size"]:
                features["acc"] = 0
            is_after_filler = True

        elif is_after_filler:
            if features["pos"] == "名詞":
                features["chain_flag"] = 0
            is_after_filler = False
        modified_njd.append(features)

    return modified_njd
