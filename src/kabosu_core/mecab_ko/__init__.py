from fugashi import GenericTagger

def try_import_ko_dic():
    try:
        import mecab_ko_dic 
        return mecab_ko_dic.MECAB_ARGS
    
    except ImportError:
        return

class Tagger(GenericTagger):
    def __init__ (self, rawargs: str = ""):
        args = rawargs
        args = try_import_ko_dic() + args
        self.tagger = GenericTagger(args)

    def parse(self, text: str):
        return self.tagger.parse(text)