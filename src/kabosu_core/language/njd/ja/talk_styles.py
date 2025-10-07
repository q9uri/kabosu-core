from kabosu_core.language.types import NjdObject

def convert_to_babytalk(
    njd_features: list[NjdObject]
) -> list[NjdObject]:
    
    features = []

    for njd_feature in njd_features:


        read = njd_feature["read"] 
        pron = njd_feature["pron"] 


        _feature = {"pron" : pron, "read" : read}

        for feature_key in njd_feature.keys():
            if feature_key == "pron":
                continue
            elif feature_key == "read":
                continue
            else:
                _feature[feature_key] = njd_feature[feature_key]

        features.append(_feature)

    return features