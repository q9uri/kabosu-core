from kabosu_core import language as  pyopenjtalk



def test_yomikata_reader_furigana_test():
    text = 'そして、畳の表は、すでに幾年前に換えられたのか分らなかった。'
    output = pyopenjtalk.reader_furigana(text)
    assert output == "そして、畳の{表/おもて}は、すでに幾年前に換えられたのか分らなかった。"

def test_yomikata_dictreader_furigana_test():
    text = 'そして、畳の表は、すでに幾年前に換えられたのか分らなかった。'
    output = pyopenjtalk.dictreader_furigana(text)
    assert output == "そして、{畳/たたみ}の{表/ひょう}は、すでに{幾/いく}{年/ねん}{前/まえ}に{換/か}えられたのか{分/わか}らなかった。"

def test_kanalizer_convert_test():
    output = pyopenjtalk.kanalizer_convert("lemon")
    assert output == "レモン"
    print(output)

def test_g2p_yomikata():
    text = pyopenjtalk.normalize_text("そして、畳の表は、すでに幾年前に換えられたのか分らなかった。")
    output = pyopenjtalk.g2p(text, kana=True)
    assert output == "ソシテ、タタミノオモテハ、スデニイクネンマエニカエラレタノカワカラナカッタ、"

def test_g2p_hungl():
    text = pyopenjtalk.normalize_text("이봐, 센파이. 한국으로 여행하자? 현지의 맛있는 요리를 먹으면 좋겠다.")
    output = pyopenjtalk.g2p(text, kana=True)
    assert output == "イブァ、センパイ、ハンググロヨヘンハザ？ホンジウィマジンヌンオリルルモグモンソゲッッタ、"
    print(output)

def test_g2p_kanalizer():
    text = pyopenjtalk.normalize_text("you are so cute! mii-chan!")
    output = pyopenjtalk.g2p(text, kana=True)
    assert output == "ユーアーソーキュート、ミイ、チャン、"

def test_njd_features_to_keihan():

    fullcontext = pyopenjtalk.extract_fullcontext("ぎょうさんおるねんな")
    kansai_fullcontext = pyopenjtalk.extract_fullcontext("ぎょうさんおるねんな", keihan=True)
    assert fullcontext != kansai_fullcontext

def test_njd_features_to_babytalk():

    fullcontext = pyopenjtalk.extract_fullcontext("可愛い赤ちゃんですねー。触ってもいいですか？")
    babytalk_fullcontext = pyopenjtalk.extract_fullcontext("可愛い赤ちゃんですねー。触ってもいいですか？", babytalk=True)
    assert fullcontext != babytalk_fullcontext

def test_njd_features_to_dakuten():

    fullcontext = pyopenjtalk.extract_fullcontext("それでも、僕は知らないッ")
    dakuten_fullcontext = pyopenjtalk.extract_fullcontext("それでも、僕は知らないッ",  dakuten=True)
    assert fullcontext != dakuten_fullcontext

