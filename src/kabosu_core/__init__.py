from .itaiji import normalize_itaiji
from .ojt_plus import apply_postprocessing
from .types import NjdObject

from pathlib import Path
import re

import jpreprocess 
import kanalizer
import jaconv
from yomikata.dbert import dBert
from yomikata.dictionary import Dictionary



#----------------------------------------------------
#
#> Copyright (c) 2018: Ryuichi Yamamoto.
#>
#> Permission is hereby granted, free of charge, to any person obtaining
#> a copy of this software and associated documentation files (the
#> "Software"), to deal in the Software without restriction, including
#> without limitation the rights to use, copy, modify, merge, publish,
#> distribute, sublicense, and/or sell copies of the Software, and to
#> permit persons to whom the Software is furnished to do so, subject to
#> the following conditions:
#>
#> The above copyright notice and this permission notice shall be
#> included in all copies or substantial portions of the Software.
#>
#> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#> EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#> MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#> IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
#> CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#> TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#> SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#/bAmFru).

from collections.abc import Callable, Generator
from contextlib import AbstractContextManager, ExitStack, contextmanager
from typing import Any, TypeVar, Union
from threading import Lock

_T = TypeVar("_T")

def _global_instance_manager(
    instance_factory: Union[Callable[[], _T], None] = None,
    instance: Union[_T, None] = None,
) -> Callable[[], AbstractContextManager[_T]]:
    assert instance_factory is not None or instance is not None
    _instance = instance
    mutex = Lock()

    @contextmanager
    def manager() -> Generator[_T, None, None]:
        nonlocal _instance
        with mutex:
            if _instance is None:
                _instance = instance_factory()  # type: ignore
            yield _instance

    return manager

# Global instance of OpenJTalk
_global_jpreprocess = _global_instance_manager(lambda: jpreprocess.jpreprocess())
# Global instance of Marine
_global_marine = None

def load_marine_model(model_dir: Union[str, None] = None, dict_dir: Union[str, None] = None):
    global _global_marine
    if _global_marine is None:
        try:
            from marine.predict import Predictor
        except ImportError:
            raise ImportError("Please install marine by `pip install pyopenjtalk-plus[marine]`")
        _global_marine = Predictor(model_dir=model_dir, postprocess_vocab_dir=dict_dir)

def update_global_jtalk_with_user_dict(
        user_dictionary: str | Path | None = None
        ) -> None:
    """Update global openjtalk instance with the user dictionary

    Note that this will change the global state of the openjtalk module.

    """

    global _global_jpreprocess
    with _global_jpreprocess():
        _global_jpreprocess = _global_instance_manager(
            instance=jpreprocess.jpreprocess(user_dictionary=user_dictionary),
        )
#-----------------------------------------------------------

_global_reader = dBert()
_global_dictreader = Dictionary()
_FURIGANA_PATTERN = re.compile("{.+/.+}")
_ALPHABET_PATTERN = re.compile("[a-z]+")

def extract_fullcontext(
        text: str,
        hankaku: bool = True,
        itaiji: bool = True,
        yomikata: bool = True,
        kanalizer: bool = True,
        use_vanilla: bool = False,
        run_marine: bool = False,
        keihan:bool = False,
        babytalk: bool = False,
        dakuten: bool = False,
        jpreprocess: Union[jpreprocess.JPreprocess, None] = None
        ) -> list[str]:
    
    """
    ### input 
    text (str): input text  
    ## output
    => list[str] : fullcontext label
    """

    njd_features = run_frontend(
        text, 
        hankaku=hankaku,
        itaiji=itaiji,
        yomikata=yomikata, 
        kanalizer=kanalizer,
        use_vanilla=use_vanilla,
        run_marine=run_marine,
        keihan=keihan,
        babytalk=babytalk,
        dakuten=dakuten,
        jpreprocess=jpreprocess
        )
    

    return make_label(njd_features)


def g2p(
        text: str,
        hankaku: bool = True,
        itaiji: bool = True,
        yomikata: bool = True,
        kanalizer: bool = True,
        use_vanilla: bool = False,
        run_marine: bool = False,
        keihan:bool = False,
        babytalk: bool = False,
        dakuten: bool = False,
        kana: bool = False,
        join: bool = True,
        jpreprocess: Union[jpreprocess.JPreprocess, None] = None
    ):

    njd_features = run_frontend(
        text, 
        hankaku=hankaku,
        itaiji=itaiji,
        yomikata=yomikata, 
        kanalizer=kanalizer,
        run_marine=run_marine,
        keihan=keihan,
        babytalk=babytalk,
        dakuten=dakuten,
        use_vanilla=use_vanilla
    )

    
    
    if kana:
        output = ""
        for njd in njd_features:
            output += njd["read"]
        
    if not kana:
        labels = make_label(njd_features, jpreprocess=jpreprocess)
        prons = list(map(lambda s: s.split("-")[1].split("+")[0], labels[1:-1]))
        if join:
            prons = " ".join(prons)
        return prons
        
    return output

def run_frontend(
            text: str,
            hankaku: bool = True,
            itaiji: bool = True,
            kanalizer: bool = True,
            yomikata: bool = True,
            use_vanilla: bool = False,
            run_marine: bool = False,
            keihan: bool = False,
            babytalk: bool = False,
            dakuten: bool = False,
            jpreprocess: Union[jpreprocess.JPreprocess, None] = None
            ) -> list[NjdObject]:
    """
    ### input 
    text (str): input text  
    hankaku (bool) : True:
    itaiji: (bool) : True:
    kanalizer: (bool) : True:
    yomikata: (bool) : True:
    kanji_yomi: (bool) : True:
    process_odori (bool) : True:
    ## output
    => list[NjdObject] : njd_features
    """


    text = normalizer(
        text,
        hankaku=hankaku,
        itaiji=itaiji,
        kanalizer=kanalizer,
        yomikata=yomikata,
    )

    if jpreprocess is not None:
        j = jpreprocess.jpreprocess()
        njd_features = j.run_frontend(text)

        if not use_vanilla:
            njd_features = apply_postprocessing(
                text,
                njd_features=njd_features,
                run_marine=run_marine,
                use_vanilla=use_vanilla,
                keihan=keihan,
                babytalk=babytalk,
                dakuten=dakuten,
                jpreprocess=j
                )
    
    global _global_jpreprocess
    with _global_jpreprocess() as jpreprocess:
        njd_features = jpreprocess.run_frontend(text)

        if not use_vanilla:
            njd_features = apply_postprocessing(
                text,
                njd_features=njd_features,
                run_marine=run_marine,
                use_vanilla=use_vanilla,
                keihan=keihan,
                babytalk=babytalk,
                dakuten=dakuten,
                jpreprocess=jpreprocess
                )

    return njd_features


def make_label(
        njd_features: list[NjdObject], 
        jpreprocess: Union[jpreprocess.JPreprocess, None] = None
        ) -> list[str]:
    
    if jpreprocess is not None:
        j = jpreprocess.jpreprocess()
        return j.make_label(njd_features)

    global _global_jpreprocess
    with _global_jpreprocess() as jpreprocess:
        return jpreprocess.make_label(njd_features)


def reader_furigana(text:str):
    # this liblary use fork version yomikata
    # https://github.com/q9uri/yomikata

    return _global_reader.furigana(text)

def dictreader_furigana(text:str):
    return _global_dictreader.furigana(text)


def kanalizer_convert(text: str):
    return kanalizer.convert(text, on_invalid_input="warning")

def normalizer(
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

        alphabet_list = _ALPHABET_PATTERN.findall(text)
        for word in alphabet_list:
                
            yomi = kanalizer_convert(word)
            text = text.replace(word, yomi)

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
                        
    return text


