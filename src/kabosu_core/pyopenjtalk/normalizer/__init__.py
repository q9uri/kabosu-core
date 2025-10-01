
import jaconv
import re2
import kanalizer

from yomikata.dbert import dBert
from yomikata.dictionary import Dictionary

_global_reader = dBert()
_global_dictreader = Dictionary()



from kabosu_core.pyopenjtalk.normalizer.itaiji import normalize_itaiji

_FURIGANA_PATTERN = re2.compile("{.+/.+}")
_ALPHABET_PATTERN = re2.compile("[a-z]+")

def reader_furigana(text:str):
    # this liblary use fork version yomikata
    # https://github.com/q9uri/yomikata

    return _global_reader.furigana(text) #type: ignore

def dictreader_furigana(text:str):
    return _global_dictreader.furigana(text) #type: ignore


def kanalizer_convert(text: str):
    return kanalizer.convert(text, on_invalid_input="warning")

def normalize_text(
        text: str,
        hankaku: bool = True,
        itaiji: bool = True,
        kanalizer: bool = True,
        yomikata: bool = True,
        use_ko2ja: bool = True
    ) -> str:
    """
    ### input 
    text (str): input text  
    hankaku (bool): convert hankaku to zenkaku  
    itaiji (bool): convert itaiji to joyo-kanji
    ## output
    str : normalized text
    """
    
    if hankaku:
        text = jaconv.h2z(text)

    if itaiji:
        text = normalize_itaiji(text)

    if yomikata:
        furigana_text = reader_furigana(text)
        yomi_list = _FURIGANA_PATTERN.findall(furigana_text)

        for furigana in yomi_list:
            furigana = furigana.replace("{", "")
            furigana = furigana.replace("}", "")
            
            
            splited = furigana.split("/")
            word = splited[0]
            yomi = splited[1]
            
            yomi = jaconv.hira2kata(yomi)
            text = text.replace(word, yomi)
    
    if kanalizer:
        text = text.lower()

        alphabet_list = _ALPHABET_PATTERN.findall(text)
        for word in alphabet_list:
                
            yomi = kanalizer_convert(word)
            text = text.replace(word, yomi)
    
    if use_ko2ja:
        from kabosu_core.pyopenjtalk.normalizer.korean import ko2ja
        text = ko2ja(text)
        
    return text
