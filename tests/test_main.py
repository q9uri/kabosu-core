import pytest
from kabosu import Kabosu

k = Kabosu()

def test_yomikata_reader_furigana_test():
    text = 'そして、畳の表は、すでに幾年前に換えられたのか分らなかった。'
    output = k.reader_furigana(text)
    assert output == "そして、畳の{表/おもて}は、すでに幾年前に換えられたのか分らなかった。"

def test_yomikata_dictreader_furigana_test():
    text = 'そして、畳の表は、すでに幾年前に換えられたのか分らなかった。'
    output = k.dictreader_furigana(text)
    assert output == "そして、{畳/たたみ}の{表/ひょう}は、すでに{幾/いく}{年/ねん}{前/まえ}に{換/か}えられたのか{分/わか}らなかった。"

def test_kanalizer_convert_test():
    output = k.kanalizer_convert("lemon")
    assert output == "レモン"
    print(output)

def test_g2p():
    output = k.g2p("そして、畳の表は、すでに幾年前に換えられたのか分らなかった。")
    assert output == "ソシ’テ、タタミノオモテワ、スデニイクネンマエニカエラレタノカワカラナカッタ、"
    output = k.g2p("you are so cute! mii-chan!")
    assert output == "ユー、アー、ソー、キュート、、ミイ、チャン、"
    print(output)