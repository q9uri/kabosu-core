
from typing import TypedDict

# type from https://github.com/jpreprocess/jpreprocess/blob/main/bindings/python/jpreprocess/jpreprocess.pyi
class NjdObject(TypedDict):
    """
    string: str  
    pos: str  
    pos_group1: str  
    pos_group2: str  
    pos_group3: str  
    ctype: str  
    cform: str  
    orig: str  
    read: str  
    pron: str  
    acc: int  
    mora_size: int  
    chain_rule: str  
    chain_flag: int  
    """
    string: str
    pos: str
    pos_group1: str
    pos_group2: str
    pos_group3: str
    ctype: str
    cform: str
    orig: str
    read: str
    pron: str
    acc: int
    mora_size: int
    chain_rule: str
    chain_flag: int

class ExtendedNjdObject(TypedDict):
    """
    string: str  
    pos: str  
    pos_group1: str  
    pos_group2: str  
    pos_group3: str  
    ctype: str  
    cform: str  
    orig: str  
    read: str  
    pron: str
    acc: int  
    mora_size: int  
    chain_rule: str  
    chain_flag: int  
    roman: str #cutlet  
    """
    string: str
    pos: str
    pos_group1: str
    pos_group2: str
    pos_group3: str
    ctype: str
    cform: str
    orig: str
    read: str
    pron: str
    acc: int
    mora_size: int
    chain_rule: str
    chain_flag: int
    roman: str #cutlet
    

class ExtractedJpObject(TypedDict):
    """
    text: str  
    text_bak: str #korean, english etc.  before convert strings.  
    asa: list[tuple[str, str]]  
    words: list[ExtendedNjdObject]  
    """
    text: str
    text_bak: str #korean, english etc.  before convert strings.
    asa: list[tuple[str, str]]
    words: list[ExtendedNjdObject]

class Language(TypedDict):
    """
    """
    ja:str = "ja" #日本語
    ko:str = "ko" #韓国語

    zh:str = "zh"
    eo:str = "eo" #エスペラント語

    en:str = "en" #英語
    es:str = "es" #スペイン語
    fr:str = "fr" #フランス語
    it:str = "it" #イタリア語
    de:str = "de" #ドイツ語
    la:str = "la" #ラテン語
    ru:str = "ru" #ロシア語
