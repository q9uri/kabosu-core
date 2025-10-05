from typing import Literal
from kabosu_core.asseets import (
    UNIDIC_LITE_DIR,
    IPADIC_DIR,
    JUMANDIC_DIR,
    KO_DIC_DIR
)

class Tagger():
    def __init__ (
            self,
            dictionary:Literal[
                "ko-dic",
                "jumandic",
                "ipa-dic",
                "unidic-lite"
                ] = "ko-dic", 
            rawargs: str = ""
            ):
        

        self.dictionary = dictionary
        
        if self.dictionary in ("ipa-dic", "jumandic", "unidic-lite", "ko-dic"):
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

            elif self.dictionary == "ko-dic":
               
                with open(KO_DIC_DIR, 'rb') as fp:
                    with dctx.stream_reader(fp) as dict_reader:
                        self.tagger = vibrato.Vibrato(dict_reader.read())



    def __call__ (self, text:str = "", out_list:bool = True):
        if self.dictionary in ("ipa-dic", "jumandic", "unidic-lite", "ko-dic"):
            tokens = self.tagger.tokenize(text)
            if out_list:
                out = []
                for token in tokens:
                    surface = token.surface()
                    feature_list = token.feature().split(",")
                    cur_word_list = [surface] + feature_list
                    out.append(cur_word_list)
                        
                return out
            
            else:
                return tokens

    def parse(self, text: str) -> list[str]:

        if self.dictionary in ("ipa-dic", "jumandic", "unidic-lite", "ko-dic"):
            tokens = self.tagger.tokenize(text)
            out = []
            for token in tokens:
                surface = token.surface()
                feature = token.feature().replace(",", "\t")
                out_text = "\t".join( ( surface, feature ) )
                out.append(out_text)

            return "\n".join(out)
