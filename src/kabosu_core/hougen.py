from .types import NjdObject

def convert_to_keihan_acc(
    njd_features: list[NjdObject]
) -> list[NjdObject]:
    
    # https://www.akenotsuki.com/kyookotoba/accent/taihi.html#S2
    # 一泊ずらし
    # ずらせない特殊なアクセント対応表:
    # tokyo acc0, mora3 == LHH, :keihan HHH
    # tokyo acc0 , mora3== LLH, :keihan HHH
    #「雪が・山が・川が」等acc1, mora3 chain_flag = 0, = tokyo LHL, :keihan HLL 
    features = []

    for node_index, njd_feature in enumerate(njd_features):
        mora_size = njd_feature["mora_size"] 
        acc = njd_feature["acc"] 
        chain_flag = njd_feature["chain_flag"] 
        if acc != 0 and acc != mora_size:
            if chain_flag == -1:
                _feature["acc"] = acc + 1
            elif chain_flag == 0:
                _feature["acc"] = 1

        _feature = {}
        for feature_key in njd_feature.keys():
            if feature_key != "acc":
                _feature[feature_key] = njd_feature[feature_key]
        features.append(_feature)

    return features