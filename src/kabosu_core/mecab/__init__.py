from fugashi import GenericTagger
from typing import Literal
from pathlib import Path
import os

def try_import_ko_dic():
    try:
        import mecab_ko_dic 
        return mecab_ko_dic.MECAB_ARGS
    
    except ImportError:
        return

class Tagger():
    def __init__ (
            self,
            text:str = "",
            dictionary:Literal[
                "ko-dic",
                "jumandic",
                "ipa-dic",
                "unidic-lite"
                ] = "ko-dic", 
            rawargs: str = ""
            ):
        self.text = text
        CUR_DIR = Path(os.path.dirname(__file__))
        DICT_DIR = CUR_DIR / "dict"
        
        UNIDIC_LITE_DIR = DICT_DIR / "unidic-mecab-2-1-2/system.dic.zst"
        IPADIC_DIR = DICT_DIR / "unidic-mecab-2-1-2/system.dic.zst"
        JUMANDIC_DIR = DICT_DIR / "unidic-mecab-2-1-2/system.dic.zst"

        self.dictionary = dictionary
        if self.dictionary == "ko-dic":
            args = rawargs
            args = try_import_ko_dic() + args
            self.tagger = GenericTagger(args)
        
        elif self.dictionary in ("ipa-dic", "jumandic", "unidic-lite"):
            import vibrato
            import zstandard
            dctx = zstandard.ZstdDecompressor()

            if self.dictionary == "ipa-dic":
                
                with open(IPADIC_DIR, 'rb') as fp:
                    with dctx.stream_reader(fp) as dict_reader:
                        self.tagger = vibrato.Vibrato(dict_reader.read())

            
            elif self.dictionary == "jumandic":
               
                with open(JUMANDIC_DIR, 'rb') as fp:
                    with dctx.stream_reader(fp) as dict_reader:
                        self.tagger = vibrato.Vibrato(dict_reader.read())
      

            elif self.dictionary == "unidic-lite":
               
                with open(UNIDIC_LITE_DIR, 'rb') as fp:
                    with dctx.stream_reader(fp) as dict_reader:
                        self.tagger = vibrato.Vibrato(dict_reader.read())
                        
    def __call__ (self):
        tokens = self.tagger.tokenize(self.text)

        out = []
        for token in tokens:
            surface = token.surface()
            feature_list = token.feature().split(",")
            cur_word_list = [surface] + feature_list
            out.append(cur_word_list)
                
        return out

    def parse(self, text: str) -> list[str]:
        if self.dictionary == "ko-dic":

            return self.tagger.parse(text)
        
        elif self.dictionary in ("ipa-dic", "jumandic", "unidic-lite"):
            tokens = self.tagger.tokenize(text)
            out = []
            for token in tokens:
                surface = token.surface()
                feature = token.feature().replace(",", "\t")
                out_text = "\t".join( ( surface, feature ) )
                out.append(out_text)

            return "\n".join(out)
