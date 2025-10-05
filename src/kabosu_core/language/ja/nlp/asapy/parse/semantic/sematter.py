from kabosu_core.language.ja.nlp.asapy.result import Result
from kabosu_core.language.ja.nlp.asapy.result import Chunk
from kabosu_core.language.ja.nlp.asapy.parse.semantic.calculate import Calculate
from kabosu_core.language.ja.nlp.asapy.parse.semantic.adjunct import Adjunct
from kabosu_core.language.ja.nlp.asapy.parse.semantic.noun_structure import NounStructure
from kabosu_core.language.ja.nlp.asapy.load import LoadJson


# 語義，意味役割を付与するためのクラス


class Sematter():

    def __init__(self, loadedjson: LoadJson) -> None:
        self.frames = loadedjson.frames
        self.nouns = loadedjson.nouns
        self.loadedjson = loadedjson
        self.calc = Calculate(self.frames)
        self.adjunct = Adjunct()
        self.nounstruct = NounStructure(loadedjson)

    def parse(self, result: Result) -> None:
        verbchunks = self.__getSemChunks(result)
        for verbchunk in verbchunks:
            linkchunks = self.__getLinkChunks(verbchunk)
            self.__setAnotherPart(linkchunks)
            frame = self.calc.getFrame(verbchunk.main, linkchunks)
            if frame:
                semantic, similar, insts = frame
                self.__setSemantic(semantic, similar, verbchunk)
                self.__setSemRole(insts)
                self.__setArg(insts)
                self.__setSpecialSemantic(verbchunk)
                self.adjunct.parse(verbchunk.modifiedchunks)
        nounchunks = self.__getNounChunks(result)
        for nounchunk in nounchunks:
            self.nounstruct.parse(nounchunk)
        self.__setInversedSemantic(result)
        return result

    #
    # 係り先である節を取得
    #
    def __getSemChunks(self, result: Result) -> list:
        chunks = [c for c in result.chunks if c.ctype != 'elem' and self.loadedjson.isframe(c.main)]
        return chunks

    #
    # 係り先の節を渡して，その係り元を取得
    #
    def __getLinkChunks(self, verbchunk: Chunk) -> list:
        if verbchunk.modifyingchunk and (verbchunk.modifyingchunk.ctype == 'elem'):
            can = [c.part for c in verbchunk.modifiedchunks]
            verbchunk.modifyingchunk.another_parts = {'が', 'を', 'に'} - set(can)
            verbchunk.modifiedchunks.append(verbchunk.modifyingchunk)
        return verbchunk.modifiedchunks

    #
    # 助詞の言い換え候補があるものに対して，言い換えの助詞を付与
    #
    def __setAnotherPart(self, chunks: list) -> None:
        for chunk in chunks:
            for morph in chunk.morphs:
                if '格助詞' in morph.pos and chunk.part in {'に', 'へ'}:
                    chunk.another_parts = list({'に', 'へ'} - set(chunk.part))
                elif '係助詞' in morph.pos:
                    chunk.another_parts = ['が', 'を']
                else:
                    pass

    #
    # 曖昧性を解消したフレームのデータより語義を付与
    # @param semantic Calculateクラスより取得したデータ
    # @param verbchunk 語義を付与する文節
    #
    def __setSemantic(self, semantic: str, similar: float, verbchunk: Chunk) -> None:
        verbchunk.semantic = semantic
        verbchunk.similar = similar

    #
    # 曖昧性を解消したフレームのデータより意味役割を付与
    # @param semantic Calculateクラスより取得したデータ
    #
    def __setSemRole(self, insts: list) -> None:
        for instset in insts:
            similar, icase, chunk = instset
            chunk.semrole.append(icase['semrole'])
            chunk.similar = similar
            if icase['category'] in chunk.category:
                chunk.category.append(icase['category'])
                chunk.category = list(set(chunk.category))

    def __setArg(self, insts: list) -> None:
        for instset in insts:
            similar, icase, chunk = instset
            if icase['arg']: chunk.arg.append(icase['arg'])
            chunk.similar = similar
            if icase['category'] in chunk.category:
                chunk.category.append(icase['category'])
                chunk.category = list(set(chunk.category))

    def __setSpecialSemantic(self, chunk: Chunk) -> None:
        semantics = (chunk.semantic.split('-') + ['' for i in range(5)])[:5]
        if semantics[1] == '位置変化' and semantics[3] == '着点への移動':
            if any([True if '対象' in c.semrole else False  for c in chunk.modifiedchunks]):
                pass
            else:
                for c in chunk.modifiedchunks:
                    if c.part == 'が':
                        c.semrole.append('対象')
        elif semantics[1] == '位置変化' and semantics[2] == '位置変化（物理）（人物間）' and semantics[3] == '他者からの所有物の移動':
            if any([True if '着点' in c.semrole else False  for c in chunk.modifiedchunks]):
                pass
            else:
                for c in chunk.modifiedchunks:
                    if '動作主' in c.semrole or '経験者' in c.semrole:
                        c.semrole.append('着点')

    def __getNounChunks(self, result: Result) -> list:
        chunks = [chunk for chunk in result.chunks if self.loadedjson.isframe_noun(chunk.main)]
        return chunks

    def __setInversedSemantic(self, result: Result) -> None:
        for chunk in result.chunks:
            self.__getModChunk(chunk)

    def __getModChunk(self, chunk: Chunk) -> None:
        if chunk.modifyingchunk:
            chunk.modifiedchunks.append(chunk.modifyingchunk)
