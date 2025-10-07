from kabosu_core.language.types import NjdObject
from kabosu_core.language.njd.ja.tables.talk_style import (
    TO_BABYTALK_LIST,
    TO_DAKUION_LIST
)
from typing import Literal

def convert_talkstyle(
    njd_features: list[NjdObject],
    talkstyle: Literal["babytalk", "dakuon"]
) -> list[NjdObject]:
    
    features = []

    for njd_feature in njd_features:


        read = njd_feature["read"] 
        pron = njd_feature["pron"]
        if talkstyle == "dakuon":
            for before, after in TO_DAKUION_LIST:
                pron = pron.replace(before, after)
                read = read.replace(before, after)
        
        elif talkstyle == "babytalk":
            for before, after in TO_BABYTALK_LIST:
                pron = pron.replace(before, after)
                read = read.replace(before, after)

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