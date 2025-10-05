from kabosu_core.language.ja.nlp.asapy.parse.analyzer import Analyzer
from kabosu_core.language.ja.nlp.asapy.parse.analyzer.Basic import Basic
from kabosu_core.language.ja.nlp.asapy.parse.feature import Tagger
from kabosu_core.language.ja.nlp.asapy.parse.idiom import Hiuchi
from kabosu_core.language.ja.nlp.asapy.parse.semantic.sematter import Sematter
from kabosu_core.language.ja.nlp.asapy.parse.compound_predicate import Synonym
from kabosu_core.language.ja.nlp.asapy.result import Result
from kabosu_core.language.ja.nlp.asapy.load import LoadJson


class Parse():

    def __init__(self, dicts: LoadJson, analyzertype: str) -> None:
        self.analyzer = Analyzer(analyzertype, "utf-8")
        self.basic = Basic(dicts.frames)
        self.tagger = Tagger(dicts.ccharts, dicts.categorys)
        self.idiom = Hiuchi(dicts.idioms, dicts.filters)
        self.sematter = Sematter(dicts)
        self.compoundPredicate = Synonym(dicts.compoundPredicates, dicts.filters)

    def parse(self, line: str) -> Result:
        result = self.__parseChunk(line)
        result = self.__parseFeature(result)
        result = self.__parseIdiom(result)
        result = self.__parseSemantic(result)
        result = self.__parseCompoundPredicate(result)
        return result

    # cabochaを利用し文を文節と形態素を解析
    # また解析結果より相互関係や動詞などの情報を整理
    def __parseChunk(self, line: str) -> Result:
        result = self.analyzer.parse(line)
        self.basic.parse(result)
        return result

    # 態や名詞カテゴリなどを付与
    def __parseFeature(self, result: Result) -> Result:
        self.tagger.parse(result)
        return result

    # 慣用句の同定を行い，フィルタリングをする
    def __parseIdiom(self, result: Result) -> Result:
        self.idiom.parse(result)
        return result

    # 語義や意味役割の付与
    def __parseSemantic(self, result: Result) -> Result:
        self.sematter.parse(result)
        return result

    # 複合述語の同定を行い，一部の語義と意味役割を上書きする
    def __parseCompoundPredicate(self, result: Result) -> Result:
        self.compoundPredicate.parse(result)
        return result