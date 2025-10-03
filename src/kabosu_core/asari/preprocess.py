from kabosu_core import mecab

t = mecab.Tagger(dictionary="ipa-dic")


def tokenize(text: str) -> str:
    return " ".join([ i[0] for i in t(text)])
