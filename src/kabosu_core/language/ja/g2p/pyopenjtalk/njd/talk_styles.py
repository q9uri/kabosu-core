from kabosu_core.types import NjdObject

def convert_to_babytalk(
    njd_features: list[NjdObject]
) -> list[NjdObject]:
    
    features = []

    for njd_feature in njd_features:


        read = njd_feature["read"] 
        pron = njd_feature["pron"] 

        pron = pron.replace("タ", "チャ")
        read = read.replace("タ", "チャ")

        pron = pron.replace("ツ", "チュ")
        read = read.replace("ツ", "チュ")

        pron = pron.replace("テ", "チェ")
        read = read.replace("テ", "チェ")

        pron = pron.replace("ト", "チョ")
        read = read.replace("ト", "チョ")

        pron = pron.replace("サ", "チャ")
        read = read.replace("サ", "チャ")

        pron = pron.replace("シ", "チ")
        read = read.replace("シ", "チ")

        pron = pron.replace("ス", "チュ")
        read = read.replace("ス", "チュ")

        pron = pron.replace("セ", "チェ")
        read = read.replace("セ", "チェ")

        pron = pron.replace("ソ", "チョ")
        read = read.replace("ソ", "チョ")
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

def convert_to_dakuten(
    njd_features: list[NjdObject]
) -> list[NjdObject]:
    
    features = []

    for njd_feature in njd_features:


        read = njd_feature["read"] 
        pron = njd_feature["pron"] 

        pron = pron.replace("タ", "ダ")
        read = read.replace("タ", "ダ")

        pron = pron.replace("チ", "ヂ")
        read = read.replace("チ", "ヂ")

        pron = pron.replace("ツ", "ヅ")
        read = read.replace("ツ", "ヅ")

        pron = pron.replace("テ", "デ")
        read = read.replace("テ", "デ")

        pron = pron.replace("ト", "ド")
        read = read.replace("ト", "ド")

        pron = pron.replace("カ", "ガ")
        read = read.replace("カ", "ガ")

        pron = pron.replace("キ", "ギ")
        read = read.replace("キ", "ギ")

        pron = pron.replace("ク", "グ")
        read = read.replace("ク", "グ")

        pron = pron.replace("ケ", "ゲ")
        read = read.replace("ケ", "ゲ")

        pron = pron.replace("コ", "ゴ")
        read = read.replace("コ", "ゴ")

        pron = pron.replace("サ", "ザ")
        read = read.replace("サ", "ザ")

        pron = pron.replace("シ", "ジ")
        read = read.replace("シ", "ジ")

        pron = pron.replace("ス", "ズ")
        read = read.replace("ス", "ズ")

        pron = pron.replace("セ", "ゼ")
        read = read.replace("セ", "ゼ")

        pron = pron.replace("ソ", "ゾ")
        read = read.replace("ソ", "ゾ")

        pron = pron.replace("ハ", "バ")
        read = read.replace("ハ", "バ")

        pron = pron.replace("ヒ", "ビ")
        read = read.replace("ヒ", "ビ")

        pron = pron.replace("フ", "ブ")
        read = read.replace("フ", "ブ")

        pron = pron.replace("ヘ", "ベ")
        read = read.replace("ヘ", "ベ")

        pron = pron.replace("ホ", "ボ")
        read = read.replace("ホ", "ボ")


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