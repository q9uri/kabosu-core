import spacy
from ginza.analyzer import format_cabocha

from kabosu_core.language.njd.ja.lib.asapy.result import Result
from kabosu_core.language.njd.ja.lib.asapy.result import Chunk
from kabosu_core.language.njd.ja.lib.asapy.result import Morph



class Analyzer():

    def __init__(self, analyzertype: str, code: str) -> None:
        if analyzertype == 'cabocha':
            self.analyzer = spacy.load('ja_ginza')

    def parse(self, line: str) -> Result:
        m_id = 0
        result = Result(line)

        doc = self.analyzer(line)
        out_str = ""
        for sents in doc.sents:
            out_str += format_cabocha(sents, use_normalized_form=True)
        line_list = out_str.split("\n")
        line_list.append("EOS")
         
        for line in line_list:
            if line == "EOS":
                break
            if line.startswith("* "):
                result.addChunk(Chunk(line))
                m_id = 0
            elif line != "EOS":
                result.chunks[-1].addMorph(Morph(m_id, line))
                m_id += 1
        return result
