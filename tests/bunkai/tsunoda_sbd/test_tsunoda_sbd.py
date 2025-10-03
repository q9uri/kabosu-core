
from kabosu_core.bunkai.algorithm.tsunoda_sbd.tsunoda_sbd import TsunodaSentenceBoundaryDisambiguation
from kabosu_core.bunkai.base.annotation import Annotations


def test_okay():
    splitter_obj = TsunodaSentenceBoundaryDisambiguation()

    test_sentence_1_ok = (
        "これ、テスト文なんですけど(笑)"
        "本当?にこんなテキストでいいのかな☆"
        "10秒で考えて書いたよ."
        "(セルフドリンクサービスはすごく良かったです!種類も豊富。)"
        "おすすめ度No.1の和室3.5畳はあります。"
        "おしまい♪"
        "(近日中には冷房に切り替わる予定です。いいですね(泣))"
    )
    assert (isinstance(splitter_obj.eos(test_sentence_1_ok), Annotations)) == True
    assert len(splitter_obj.eos(test_sentence_1_ok).get_final_layer()) == 7 
    assert len(splitter_obj.find_eos(test_sentence_1_ok)) == 7
    assert len(list(splitter_obj(test_sentence_1_ok))) == 7
