# -*- coding: utf-8 -*-


import re


from nltk.corpus.util import LazyCorpusLoader
from nltk.corpus.reader.cmudict import CMUDictCorpusReader

from kabosu_core.language.njd.ko.jamo import h2j, j2hcj
#from nltk.corpus import cmudict
from kabosu_core.language import vibrato as MeCab

# For further info. about cmu dict, consult http://www.speech.cs.cmu.edu/cgi-bin/cmudict.
# try:
#    nltk.data.find('corpora/cmudict.zip')
# except LookupError:
#    nltk.download('cmudict')
# included cmudict

from kabosu_core.language.ko.g2p.special import jyeo, ye, consonant_ui, josa_ui, vowel_ui, jamo, rieulgiyeok, rieulbieub, verb_nieun, balb, palatalize, modifying_rieul
from kabosu_core.language.ko.g2p.regular import link1, link2, link3, link4
from kabosu_core.language.ko.g2p.utils import annotate, compose, group, gloss, parse_table, get_rule_id2text
from kabosu_core.language.ko.g2p.normalaizer.english import convert_eng
from kabosu_core.language.ko.g2p.normalaizer.numerals import convert_num

#==============================================================
#added from kdrkdrkdr/g2pk3
from kabosu_core.language.ko.g2p.normalaizer.japanese import convert_jpn
from kabosu_core.language.ko.g2p.korean import join_jamos, split_syllables
#=============================================================

from kabosu_core.asseets import G2PK4_DICT_DIR, NLTK_DIR


class G2p(object):
    def __init__(self,):
        
        self.vibrato = MeCab.Tagger()
        self.table = parse_table()



        cmudict = LazyCorpusLoader(name="cmudict",
                                    reader_cls=CMUDictCorpusReader,
                                    nltk_data_subdir=NLTK_DIR,
                                    fileids=["cmudict"]
                                    )
        self.cmu = cmudict.dict() # for English

        self.rule2text = get_rule_id2text() # for comments of main rules
        self.idioms_path = (G2PK4_DICT_DIR / "idioms.txt")

    def load_module_func(self, module_name):
        tmp = __import__(module_name, fromlist=[module_name])
        return tmp


    def idioms(self, string, descriptive=False, verbose=False):
        '''Process each line in `idioms.txt`
        Each line is delimited by "===",
        and the left string is replaced by the right one.
        inp: input string.
        descriptive: not used.
        verbose: boolean.

        >>> idioms("지금 mp3 파일을 다운받고 있어요")
        지금 엠피쓰리 파일을 다운받고 있어요
        '''
        rule = "from idioms.txt"
        out = string

        with open(self.idioms_path, 'r', encoding="utf8") as f:
            for line in f:
                line = line.split("#")[0].strip()
                if "===" in line:
                    str1, str2 = line.split("===")
                    out = re.sub(str1, str2, out)
            gloss(verbose, out, string, rule)

        return out

    def __call__(self,
                string, 
                descriptive: bool  = False,
                verbose: bool = False,
                group_vowels: bool  = False,
                to_syl: bool = True,
                to_hcj: bool = False,
                convert_japanese: bool = True,
                convert_english: bool = True,
                ) -> str | list[list[str]]:
        '''Main function
        string: input string
        descriptive: boolean.
        verbose: boolean
        group_vowels: boolean. If True, the vowels of the identical sound are normalized.
        to_syl: boolean. If True, hangul letters or jamo are assembled to form syllables.

        For example, given an input string "나의 친구가 mp3 file 3개를 다운받고 있다",
        STEP 1. idioms
        -> 나의 친구가 엠피쓰리 file 3개를 다운받고 있다

        STEP 2. English to Hangul
        -> 나의 친구가 엠피쓰리 파일 3개를 다운받고 있다

        STEP 3. annotate
        -> 나의/J 친구가 엠피쓰리 파일 3개/B를 다운받고 있다

        STEP 4. Spell out arabic numbers
        -> 나의/J 친구가 엠피쓰리 파일 세개/B를 다운받고 있다

        STEP 5. decompose
        -> 나의/J 친구가 엠피쓰리 파일 세개/B를 다운받고 있다

        STEP 6-9. Hangul
        -> 나의 친구가 엠피쓰리 파일 세개를 다운받꼬 읻따
        '''
        # 1. idioms
        string = self.idioms(string, descriptive, verbose)

        # 2 English and Japanese to Hangul
        if convert_english:
            string = convert_eng(string, self.cmu)
        if convert_japanese:
            string = convert_jpn(string)

        # 3. annotate
        string = annotate(string, self.vibrato)


        # 4. Spell out arabic numbers
        string = convert_num(string)

        # 5. decompose
        inp = h2j(string)

        # 6. special
        for func in (jyeo, ye, consonant_ui, josa_ui, vowel_ui, \
                     jamo, rieulgiyeok, rieulbieub, verb_nieun, \
                     balb, palatalize, modifying_rieul):
            inp = func(inp, descriptive, verbose)
        inp = re.sub("/[PJEB]", "", inp)

        # 7. regular table: batchim + onset
        for str1, str2, rule_ids in self.table:
            _inp = inp
            inp = re.sub(str1, str2, inp)

            if len(rule_ids)>0:
                rule = "\n".join(self.rule2text.get(rule_id, "") for rule_id in rule_ids)
            else:
                rule = ""
            gloss(verbose, inp, _inp, rule)

        # 8 link
        for func in (link1, link2, link3, link4):
            inp = func(inp, descriptive, verbose)

        #==============================================================
        # added from kdrkdrkdr/g2pk3
        # 8.5 Error Fix, 제 20항 적용 오류 해결
        inp_ = ""
        inp = split_syllables(inp.strip())
        i = 0
        while i < len(inp) - 4:
            if (inp[i:i+3] == 'ㅇㅡㄹ' or inp[i:i+3] == 'ㄹㅡㄹ') and inp[i+3] == ' ' and inp[i+4] == 'ㄹ':
                inp_ += inp[i:i+3] + ' ' + 'ㄴ'
                i += 5
            else:
                inp_ += inp[i]
                i += 1
        inp_ += inp[i:]
        inp = join_jamos(inp_)        # 8.5 Error Fix, 제 20항 적용 오류 해결
        inp_ = ""
        inp = split_syllables(inp.strip())
        i = 0
        while i < len(inp) - 4:
            if (inp[i:i+3] == 'ㅇㅡㄹ' or inp[i:i+3] == 'ㄹㅡㄹ') and inp[i+3] == ' ' and inp[i+4] == 'ㄹ':
                inp_ += inp[i:i+3] + ' ' + 'ㄴ'
                i += 5
            else:
                inp_ += inp[i]
                i += 1
        inp_ += inp[i:]
        inp = join_jamos(inp_)
        #==============================================================

        # 9. postprocessing
        if group_vowels:
            inp = group(inp)

        if to_syl:
            inp = compose(inp)

        if to_hcj:

            out = []

            for word in inp.split():
                word_list = []

                for i in range(len(word)):
                    chr = word[i]
                    cur_jamo = j2hcj(h2j(chr))
                    word_list.append(cur_jamo)

                out.append(word_list)

            return out

                

        return inp

if __name__ == "__main__":
    g2p = G2p()
    a = g2p("나의 친구가 mp3 file 3개를 다운받고 있다")

    print(a)