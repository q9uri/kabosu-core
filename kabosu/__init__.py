from .itaiji import normalize_itaiji

from pathlib import Path
import re

from typing import TypedDict
import jpreprocess 
import kanalizer
import jaconv
from yomikata.dbert import dBert
from yomikata.dictionary import Dictionary

# type from https://github.com/jpreprocess/jpreprocess/blob/main/bindings/python/jpreprocess/jpreprocess.pyi
class NjdObject(TypedDict):
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


class Kabosu:
    def __init__(
            self, 
            dictionary: str | Path | None = None,
            user_dictionary: str | Path | None = None
            ):
        """
        user_dictionary (str | Path): user dictionary path
        """
        if user_dictionary != None:
            self.jprepocess = jpreprocess.jpreprocess(dictionary = dictionary,user_dictionary=user_dictionary)
        else:
            self.jprepocess = jpreprocess.jpreprocess()
        #yomikata
        self.reader = dBert()
        self.dictreader = Dictionary()
        self._FURIGANA_PATTERN = re.compile("{.+/.+}")
        self._ALPHABET_PATTERN = re.compile("[a-z]+")
    
    
    def extract_fullcontext(self, 
                            text: str,
                            hankaku: bool = True,
                            itaiji: bool = True,
                            yomikata: bool = True,
                            kanalizer: bool = True,
                            ) -> list[str]:
        """
        ### input 
        text (str): input text  
        ## output
        => list[str] : fullcontext label
        """

        njd_features = self.run_frontend(text, 
                            hankaku=hankaku,
                            itaiji=itaiji,
                            yomikata=yomikata, 
                            kanalizer=kanalizer
                            )
        output = self.jprepocess.make_label(njd_features)
        return output
    
    def g2p(self,
            text: str,
            hankaku: bool = True,
            itaiji: bool = True,
            yomikata: bool = True,
            kanalizer: bool = True,
            pron: bool = True
        ):

        njd_features = self.run_frontend(text, 
                                    hankaku=hankaku,
                                    itaiji=itaiji,
                                    yomikata=yomikata, 
                                    kanalizer=kanalizer
                                    )
        output = ""
        for njd in njd_features:
            if pron:
                output += njd["pron"]
            
            else:
                output += njd["pron"]
            
        return output
    
    def run_frontend(
                self,
                text: str,
                hankaku: bool = True,
                itaiji: bool = True,
                kanalizer: bool = True,
                yomikata: bool = True,
                ) -> list[NjdObject]:
        """
        ### input 
        text (str): input text  
        ## output
        => list[NjdObject] : njd_features
        """
    

        text = self.normalizer(
            text,
            hankaku=hankaku,
            itaiji=itaiji,
            kanalizer=kanalizer,
            yomikata=yomikata,
        )
        njd_features = self.jprepocess.run_frontend(text)
        return njd_features


    def make_label(self, njd_features: list[NjdObject]) -> list[str]:

        output = self.jprepocess.make_label(njd_features)
        return output

    def reader_furigana(self, text:str):
        # this liblary use fork version yomikata
        # https://github.com/q9uri/yomikata

        output = self.reader.furigana(text)
        return output


    def dictreader_furigana(self, text:str):
        output = self.dictreader.furigana(text)
        return output
    
    def kanalizer_convert(self, text: str):
        output = kanalizer.convert(text, on_invalid_input="warning")
        return output

    def normalizer(
            self,
            text: str,
            hankaku: bool = True,
            itaiji: bool = True,
            kanalizer: bool = True,
            yomikata: bool = True,
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

        if kanalizer:
            text = text.lower()

            alphabet_list = self._ALPHABET_PATTERN.findall(text)
            for word in alphabet_list:
                    
                yomi = self.kanalizer_convert(word)
                text = text.replace(word, yomi)

        if yomikata:
            furigana_text = self.reader_furigana(text)
            yomi_list = self._FURIGANA_PATTERN.findall(furigana_text)

            for furigana in yomi_list:
                furigana = furigana.replace("{", "")
                furigana = furigana.replace("}", "")
                
                
                splited = furigana.split("/")
                word = splited[0]
                yomi = splited[1]
                
                yomi = jaconv.hira2kata(yomi)
                text = text.replace(word, yomi)
                            
        return text


