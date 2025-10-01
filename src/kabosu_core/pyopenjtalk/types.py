from typing import TypedDict

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
