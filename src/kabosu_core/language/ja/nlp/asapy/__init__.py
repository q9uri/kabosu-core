from kabosu_core.language.ja.nlp.asapy.load import LoadJson
from kabosu_core.language.ja.nlp.asapy.parse import Parse
from kabosu_core.language.ja.nlp.asapy.output import Output

class ASA():

    #@profile  # memory使用量を確認
    def __init__(self, analyzer: str = "cabocha") -> None:
        self.result = None
        self.dicts = LoadJson()
        self.parser = Parse(self.dicts, analyzer)
        self.output = Output()

    def parse(self, sentence: str) -> None:
        self.result = self.parser.parse(sentence)
        return self.result

    def get_result(self):
        return self.output.outputAll(self.result)

    def get_result_json(self):
        return self.output.outputJson(self.result)
