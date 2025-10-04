#!/usr/bin/env python3
from typing import List

#from janome.tokenizer import Token, Tokenizer
from kabosu_core import mecab

from kabosu_core.bunkai.base.annotation import Annotations, SpanAnnotation, TokenResult
from kabosu_core.bunkai.base.annotator import Annotator


class MorphAnnotatorJanome(Annotator):
    def __init__(self):
        super().__init__(rule_name=self.__class__.__name__)
        self.tokenizer = mecab.Tagger(dictionary="ipa-dic")

    def __generate(self, text: str) -> List[SpanAnnotation]:
        tokenizer_result = self.tokenizer(text)
        span_ann = []
        __start_index = 0
        for t_obj in tokenizer_result:
            assert isinstance(t_obj, list)
            __pos = t_obj[1:4]
            __length = len(t_obj[0])
            token = TokenResult(
                node_obj=t_obj,
                tuple_pos=__pos,
                word_stem=t_obj[7],
                word_surface=t_obj[0],
            )
            span_ann.append(
                SpanAnnotation(
                    rule_name=self.rule_name,
                    start_index=__start_index,
                    end_index=__start_index + __length,
                    split_string_type="janome",
                    split_string_value="token",
                    args={"token": token},
                )
            )
            __start_index += __length
        else:
            return span_ann

    def annotate(self, original_text: str, spans: Annotations) -> Annotations:
        anns = self.__generate(original_text)
        spans.add_annotation_layer(self.rule_name, anns + list(spans.flatten()))
        return spans
