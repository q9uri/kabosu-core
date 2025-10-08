
from kabosu_core.assets import ASAPY_JSON_DIR, ASAPY_TSV_DIR
import json

class LoadJson():

    def __init__(self):

        self.frames = self.__load_frame("new_argframes.tsv")  
        self.ccharts = self.__load_json("ccharts.json")
        #self.verb = "dict/verbs.json"
        self.categorys = self.__load_json("new_categorys.json")
        self.idioms = self.__load_json("idioms.json")
        self.filters = self.__load_json("filters.json")
        self.compoundPredicates = self.__load_json("compoundPredicates.json")
        self.nouns = self.__load_json("NounTest.json")

        #self.dicframe = "new_argframes.dic"
        #self.diccchart = "ccharts.dic"
        #self.dicfilter = "filters.dic"
        #"new_argframes.json"

    def __load_json(self, jsonpath: str) -> dict:
        dirname = ASAPY_JSON_DIR
        with open(str(dirname / jsonpath), 'r+') as f:
            return json.load(f)
    
    def __load_frame(self, tsvpath):
        index = {}
        data = (ASAPY_TSV_DIR / tsvpath).read_text(encoding="utf8")
        for line in data.split("\n"):
            n = line.split("\t")
            index.update({n[0]: (int(n[1]), int(n[2]))})
        return index 

    def get_frame_noun(self, noun: str) -> dict:
        frame = None
        if noun:
            for frame_ in self.noun['dict']:
                head = frame_['head'] if frame_['head'] else ''
                support = frame_['support'] if frame_['support'] else ''
                bol = (head == noun) or (head + support == noun) or (head == noun[:-1]) or (head + support == noun[:-1])
                if bol:
                    frame = frame_
                    break
        return frame
    
    
    def isframe_noun(self, noun: str) -> bool:
        bol = False
        if noun:
            for frame in self.nouns['dict']:
                head = frame['head'] if frame['head'] else ''
                support = frame['support'] if frame['support'] else ''
                bol = (head == noun) or (head + support == noun) or (head == noun[:-1]) or (head + support == noun[:-1])
                if bol:
                    break
        return bol
        
    def get_frame(self, verb: str) -> dict:
        frame = None
        if verb:
            for ins in self.noun['dict']:
                if verb in self.frame:
                    frame = ins["frame"]
                    break

        return frame
    
    def isframe(self, verb: str) -> bool:
        return verb in self.index
        