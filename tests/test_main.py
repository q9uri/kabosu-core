import pytest
import kabosu_core


def test_yomikata_reader_furigana_test():
    text = 'そして、畳の表は、すでに幾年前に換えられたのか分らなかった。'
    output = kabosu_core.reader_furigana(text)
    assert output == "そして、畳の{表/おもて}は、すでに幾年前に換えられたのか分らなかった。"

def test_yomikata_dictreader_furigana_test():
    text = 'そして、畳の表は、すでに幾年前に換えられたのか分らなかった。'
    output = kabosu_core.dictreader_furigana(text)
    assert output == "そして、{畳/たたみ}の{表/ひょう}は、すでに{幾/いく}{年/ねん}{前/まえ}に{換/か}えられたのか{分/わか}らなかった。"

def test_kanalizer_convert_test():
    output = kabosu_core.kanalizer_convert("lemon")
    assert output == "レモン"
    print(output)

def test_g2p():
    output = kabosu_core.g2p("そして、畳の表は、すでに幾年前に換えられたのか分らなかった。", kana=True)
    assert output == "ソシテ、タタミノオモテハ、スデニイクネンマエニカエラレタノカワカラナカッタ、"
    output = kabosu_core.g2p("you are so cute! mii-chan!", kana=True)
    assert output == "ユー、アー、ソー、キュート、、ミイ、チャン、"
    print(output)

def test_njd_features_to_keihan():

    fullcontext = kabosu_core.extract_fullcontext("ぎょうさんおるねんな")
    kansai_fullcontext = kabosu_core.extract_fullcontext("ぎょうさんおるねんな", keihan=True)
    assert fullcontext != kansai_fullcontext

def test_njd_features_to_babytalk():

    fullcontext = kabosu_core.extract_fullcontext("可愛い赤ちゃんですねー。触ってもいいですか？")
    babytalk_fullcontext = kabosu_core.extract_fullcontext("可愛い赤ちゃんですねー。触ってもいいですか？", babytalk=True)
    assert fullcontext != babytalk_fullcontext

def test_njd_features_to_dakuten():

    fullcontext = kabosu_core.extract_fullcontext("それでも、僕は知らないッ")
    dakuten_fullcontext = kabosu_core.extract_fullcontext("それでも、僕は知らないッ",  dakuten=True)
    assert fullcontext != dakuten_fullcontext

