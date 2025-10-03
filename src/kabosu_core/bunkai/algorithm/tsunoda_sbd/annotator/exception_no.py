#!/usr/bin/env python3
import re

from kabosu_core.bunkai.algorithm.tsunoda_sbd.annotator import constant
from kabosu_core.bunkai.base.annotation import Annotations
from kabosu_core.bunkai.base.annotator import Annotator

RE_NUMBER_WORD = re.compile(constant.NUMBER_WORD_REGEXP)


class ExceptionNo(Annotator):
    def __init__(self):
        super().__init__(rule_name=self.__class__.__name__)

    @staticmethod
    def is_exception_no(original_text: str, start_index: int, end_index: int) -> bool:
        """
        .の前にNoがあり、かつ後ろが数字で合った場合には分割を行わない.

        例: おすすめ度No.1 / ROOM No.411 .

        """
        if original_text[start_index:end_index] != "." and original_text[start_index:end_index] != "．":
            return False

        if RE_NUMBER_WORD.match(original_text[start_index - 2 : start_index]) and re.match(
            r"\d", original_text[end_index]
        ):
            return True
        return False

    def annotate(self, original_text: str, spans: Annotations) -> Annotations:
        __return_span_ann = []
        for __s in spans.get_final_layer():
            if self.is_exception_no(original_text, __s.start_index, __s.end_index):
                continue
            else:
                __s.rule_name = self.rule_name
                __return_span_ann.append(__s)
        spans.add_annotation_layer(self.rule_name, __return_span_ann)
        return spans
