#!/usr/bin/env python3
import dataclasses
import typing
import unittest

from kabosu_core.bunkai.algorithm.bunkai_sbd.annotator.basic_annotator import BasicRule
from kabosu_core.bunkai.algorithm.bunkai_sbd.annotator.constant import LAYER_NAME_FIRST
from kabosu_core.bunkai.algorithm.bunkai_sbd.annotator.emoji_annotator import EmojiAnnotator
from kabosu_core.bunkai.algorithm.bunkai_sbd.annotator.emotion_expression_annotator import EmotionExpressionAnnotator
from kabosu_core.bunkai.algorithm.bunkai_sbd.annotator.facemark_detector import FaceMarkDetector
from kabosu_core.bunkai.algorithm.bunkai_sbd.annotator.linebreak_force_annotator import LinebreakForceAnnotator
from kabosu_core.bunkai.algorithm.bunkai_sbd.bunkai_sbd import BunkaiSentenceBoundaryDisambiguation
from kabosu_core.bunkai.base.annotation import Annotations, SpanAnnotation


@dataclasses.dataclass
class TestInstance(object):
    sentences: typing.List[str]
    expected_rules: typing.Optional[typing.List[str]] = None


def monkeypatch_function(self, original_text: str, spans: Annotations):
    # tokenizerを更新する。すでにTokenize済みの結果を利用する。
    # self.linebreak_detector.reset_tokenizer(word_tokenizer_type='pre_tokenize', sentence2tokens=sentence2tokens)
    result: typing.List[int] = []

    new_spans = [s for s in spans.get_final_layer()]
    for predicted_index in result:
        char_index_start = new_spans[predicted_index].start_index
        char_index_end = new_spans[predicted_index].end_index
        ann = SpanAnnotation(
            rule_name="LinebreakExceptionAnnotator",
            start_index=char_index_start,
            end_index=char_index_end,
            split_string_type="linebreak",
            split_string_value=original_text[char_index_start:char_index_end],
        )
        new_spans.append(ann)
    spans.add_annotation_layer(self.rule_name, new_spans)

    return spans


class TestBunkaiSbd(unittest.TestCase):
    def setUp(self) -> None:
        self.test_sentences = [
            TestInstance(
                sentences=[
                    "まずは一文目(^!^)つぎに二文目(^^)これ、テスト文なんですけど(笑)本当?にこんなテキストでいいのかな☆",
                    "10秒で考えて書いたよ.",
                    "(セルフドリンクサービスはすごく良かったです!種類も豊富。)",
                    "おすすめ度No.1の和室3.5畳はあります。",
                    "おしまい♪",
                    "読点で文を分割するという場合もあります、しかし現在は対応していません。",
                    "(^ ^) (^　^) 先月泊まりましたが とてもよかったです。",
                    "(近日中には冷房に切り替わる予定です。\nいいですね(泣))",
                ]
            ),
            TestInstance(
                sentences=["30代の夫婦2組(男2.女2)です。"],
            ),
            TestInstance(
                sentences=[
                    "この値段で、こんな夕飯いいの？\n",
                    "って、くらいおいしかった！",
                ],
            ),
        ]

    def test_various_inputs(self):
        """Inputのバリエーションをテストする。Bertモデルを利用しない。"""
        test_cases = [
            TestInstance(
                sentences=[
                    "これが１文目です。。。。",
                    "そして、これが２文目…",
                    "３文目。",
                ],
                expected_rules=[EmotionExpressionAnnotator.__name__, BasicRule.__name__, LAYER_NAME_FIRST],
            ),
            TestInstance(
                sentences=[
                    "宿を予約しました♪!",
                    "まだ2ヶ月も先だけど。",
                    "早すぎかな(笑)",
                    "楽しみです★",
                ],
                expected_rules=[EmotionExpressionAnnotator.__name__, BasicRule.__name__, LAYER_NAME_FIRST],
            ),
            TestInstance(
                sentences=[
                    "宿を予約しました😄",
                    "まだ2ヶ月も先だけど😄",
                    "早すぎかな(笑)",
                    "楽しみです★",
                ],
                expected_rules=[EmotionExpressionAnnotator.__name__, EmojiAnnotator.__name__, LAYER_NAME_FIRST],
            ),
            TestInstance(
                sentences=[
                    "宿を予約しました😄😄😄",
                    "まだ2ヶ月も先だけど😄😄😄",
                    "早すぎかな(笑)",
                    "楽しみです★",
                ],
                expected_rules=[EmotionExpressionAnnotator.__name__, EmojiAnnotator.__name__, LAYER_NAME_FIRST],
            ),
            TestInstance(
                sentences=[
                    "宿を予約しました＼(^o^)／",
                    "まだ2ヶ月も先だけど。",
                    "早すぎかな(笑)",
                    "楽しみです★",
                ],
                expected_rules=[
                    EmotionExpressionAnnotator.__name__,
                    BasicRule.__name__,
                    FaceMarkDetector.__name__,
                    LAYER_NAME_FIRST,
                ],
            ),
            TestInstance(
                sentences=[
                    "この値段で、こんな夕飯いいの？\n",
                    "って、くらいおいしかった！",
                ],
                expected_rules=[
                    LAYER_NAME_FIRST,
                    LinebreakForceAnnotator.__name__,
                ],
            ),
            TestInstance(
                sentences=[
                    "\n\n",
                    "123\n",
                    "45\n\n",
                    "6\n  \n",
                    "7\n",
                ],
                expected_rules=[
                    LAYER_NAME_FIRST,
                    LinebreakForceAnnotator.__name__,
                ],
            ),
            TestInstance(
                sentences=[
                    "これは入力の入力サンプルです(^o^)",
                    "絵文字の文末記号も認識します😀",
                    "引用文も大丈夫？と思いませんか？",
                    "引用文の過剰分割を防げるんです👍",
                ],
                expected_rules=[
                    BasicRule.__name__,
                    FaceMarkDetector.__name__,
                    EmojiAnnotator.__name__,
                    LAYER_NAME_FIRST,
                ],
            ),
            TestInstance(
                [
                    "本商品はおすすめ度No.1です。",
                ],
                expected_rules=[LAYER_NAME_FIRST],
            ),
            TestInstance(
                sentences=[
                    "本商品はおすすめ度No.1です！という売り文句の新商品が出ている。",
                    "しかし、この商品は本当に信用できるのだろうか？",
                    "私はとても懐疑的である。",
                ],
                expected_rules=[BasicRule.__name__, LAYER_NAME_FIRST],
            ),
            TestInstance(
                [
                    "本商品はおすすめ度No.",
                ],
                expected_rules=[LAYER_NAME_FIRST],
            ),
        ]
        splitter_obj = BunkaiSentenceBoundaryDisambiguation(path_model=None)
        for test_case in test_cases:
            text: str = "".join(test_case.sentences)
            result = list(splitter_obj(text))
            self.assertEqual(
                result,
                test_case.sentences,
                msg=f"Expect N(sent)={test_case.sentences} " f"Result={result}",
            )
            annotations = splitter_obj.eos("".join(test_case.sentences))
            span_annotations = annotations.get_final_layer()
            self.assertEqual(
                set([s.rule_name for s in span_annotations]),  # type: ignore
                set(test_case.expected_rules),  # type: ignore
                msg=f"text={test_case.sentences}, "  # type: ignore
                f"{set([s.rule_name for s in span_annotations])} "
                f"!= {test_case.expected_rules}",
            )


if __name__ == "__main__":
    unittest.main()
