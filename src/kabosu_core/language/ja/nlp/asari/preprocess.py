from kabosu_core import vibrato

t = vibrato.Tagger(dictionary="ipa-dic")


def tokenize(text: str) -> str:
    return " ".join([ i[0] for i in t(text)])
