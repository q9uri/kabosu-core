# -*- coding: utf-8 -*-
import json
import os
from pathlib import Path

import fugashi
from bunkai import Bunkai

NEGATION = ('ない', 'ず', 'ぬ')
PARELLEL_PARTICLES = ('か', 'と', 'に', 'も', 'や', 'とか', 'だの', 'なり', 'やら')
DICT_DIR = os.path.join(os.path.dirname(__file__), 'dic')


class Analyzer(object):

    def __init__(self, mecab_args='', word_dict={}, wago_dict={}):
        self.word_dict = json.load(open(os.path.join(DICT_DIR, 'pn_noun.json')))
        if word_dict:
            self.word_dict.update(word_dict)
        self.wago_dict = json.load(open(os.path.join(DICT_DIR, 'pn_wago.json')))
        if wago_dict:
            self.wago_dict.update(wago_dict)
        from ipadic import DICDIR
        MECABRC = Path(DICDIR) / "mecabrc"
        MECAB_ARGS = '-r "{}" -d "{}"'.format(MECABRC, DICDIR)
        self.tagger = fugashi.GenericTagger(MECAB_ARGS + mecab_args)
        self.bunkai = Bunkai()

    def _lookup_wago(self, lemma, lemmas):
        if lemma in self.wago_dict:
            return lemma
        for i in range(10, 0, -1):
            wago = ' '.join(lemmas[-i:]) + ' ' + lemma
            if wago in self.wago_dict:
                return wago
        return ''

    def _has_arujanai(self, substring):
        return 'あるじゃない' in substring

    def _calc_sentiment_polarity(self, sentence):
        polarities = []
        lemmas = []
        n_parallel = 0
        substr_count = 0
        tagger_list = self.tagger(sentence)
        for i in range(len(tagger_list)):
            word = tagger_list[i]
            if i < len(tagger_list) -1:
                next_word = str(tagger_list[i+1])
            else:
                next_word = str(word)
            if 'BOS/EOS' not in word.feature:
                surface = str(word)
                substr_count += len(surface)
                feature = word.feature
                lemma = feature[6] if feature[6] != '*' else word
                wago = ''
                if lemma in self.word_dict:
                    polarity = 1 if self.word_dict[lemma] == 'p' else -1
                    n_parallel += next_word in PARELLEL_PARTICLES 
                else:
                    wago = self._lookup_wago(lemma, lemmas)
                    if wago:
                        if self.wago_dict[wago].startswith('ポジ'):
                            polarity = 1
                        else:
                            polarity = -1
                    else:
                        polarity = None
                if polarity:
                    polarities.append([wago or lemma, polarity])
                elif polarities and surface in NEGATION and \
                        not self._has_arujanai(sentence[:substr_count]):
                    polarities[-1][1] *= -1
                    if polarities[-1][0].endswith('-NEGATION'):
                        polarities[-1][0] = polarities[-1][0][:-9]
                    else:
                        polarities[-1][0] += '-NEGATION'
                    # parallel negation
                    if n_parallel and len(polarities) > 1:
                        if len(polarities) > n_parallel:
                            n_parallel = len(polarities)
                        else:
                            n_parallel = n_parallel + 1
                        if len(polarities) == n_parallel:
                            n_parallel = n_parallel + 1
                        for i in range(2, n_parallel):
                            polarities[-i][1] *= -1
                            if polarities[-i][0].endswith('-NEGATION'):
                                polarities[-i][0] = polarities[-i][0][:-9]
                            else:
                                polarities[-i][0] += '-NEGATION'
                        n_parallel = 0
                lemmas.append(lemma)
        return polarities

    def count_polarity(self, text):
        """Calculate sentiment polarity counts per sentence
        Arg:
            text (str)
        Return:
            counts (list) : positive and negative counts per sentence
        """
        counts = []
        for sentence in self.bunkai(text):
            count = {'positive': 0, 'negative': 0}
            polarities = self._calc_sentiment_polarity(sentence)
            for polarity in polarities:
                if polarity[1] == 1:
                    count['positive'] += 1
                elif polarity[1] == -1:
                    count['negative'] += 1
            counts.append(count)
        return counts

    def analyze(self, text):
        """Calculate sentiment polarity scores per sentence
        Arg:
            text (str)
        Return:
            scores (list) : scores per sentence
        """
        scores = []
        for sentence in self.bunkai(text):
            polarities = self._calc_sentiment_polarity(sentence)
            if polarities:
                scores.append(sum(p[1] for p in polarities) / len(polarities))
            else:
                scores.append(0)
        return scores

    def analyze_detail(self, text):
        """Calculate sentiment polarity scores per sentence
        Arg:
            text (str)
        Return:
            results (list) : analysis results
        """
        results = []
        for sentence in self.bunkai(text):
            polarities = self._calc_sentiment_polarity(sentence)
            if polarities:
                result = {
                    'positive': [p[0] for p in polarities if p[1] == 1],
                    'negative': [p[0] for p in polarities if p[1] == -1],
                    'score': sum(p[1] for p in polarities) / len(polarities),
                }
            else:
                result = {'positive': [], 'negative': [], 'score': 0.0}
            results.append(result)
        return results
