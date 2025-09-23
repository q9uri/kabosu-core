from .types import NjdObject

def convert_to_keihan_acc(
    njd_features: list[NjdObject]
) -> list[NjdObject]:
    
    # https://www.akenotsuki.com/kyookotoba/accent/taihi.html#S2
    # 一泊ずらし
    # ずらせない特殊なアクセント対応表:
    # この実装での独自ルール
    # acc == 0  => acc 1
    # acc == mora
    # force chainflag to 0
    features = []

    for njd_feature in njd_features:
        #force chainflag to 0
        _feature = {"chain_flag": -1}

        mora_size = njd_feature["mora_size"] 
        acc = njd_feature["acc"] 

        if acc != 0 and acc != mora_size:
            _feature["acc"] = acc + 1

        elif acc == 0 :
            _feature["acc"] = 1

        else:
            _feature["acc"] = acc

        for feature_key in njd_feature.keys():
            if feature_key == "acc":
                continue
            elif feature_key == "chain_flag":
                continue
            else:
                _feature[feature_key] = njd_feature[feature_key]

        features.append(_feature)

    return features