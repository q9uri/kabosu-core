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

    for node_index, njd_feature in enumerate(njd_features):
        _feature = {}
        mora_size = njd_feature["mora_size"] 
        acc = njd_feature["acc"] 
        if acc != 0 and acc != mora_size:
            _feature["acc"] = acc + 1
        elif acc != 0 :
            _feature["acc"] = 1
        else:
            _feature["acc"] = acc

        #force chainflag to 0
        _feature["chain_flag"] = 0

        for feature_key in njd_feature.keys():
            if feature_key != "acc":
                _feature[feature_key] = njd_feature[feature_key]
        features.append(_feature)

    return features