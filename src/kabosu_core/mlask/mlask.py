# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
import os
from pathlib import Path
import re
import collections

from  kabosu_core import mecab as MeCaB


"""
ML-Ask (eMotive eLement and Expression Analysis system) is a keyword-based language-dependent system
for automatic affect annotation on utterances in Japanese.
It uses a two-step procedure:
1. Specifying whether a sentence is emotive, and
2. Recognizing particular emotion types in utterances described as emotive.

Original Perl version by Michal Ptaszynski
Python version by Yukino Ikegami
"""


# cvs stands for "Contextual Valence Shifters"
RE_PARTICLES = '[だとはでがはもならじゃちってんすあ]*'
RE_CVS = 'いまひとつもない|なくても?問題ない|わけに[はも]?いかない|わけに[はも]?いくまい|いまひとつない|ちょ?っとも?ない|なくても?大丈夫|今ひとつもない|訳にはいくまい|訳に[はも]?[行い]かない|そんなにない|ぜったいない|まったくない|すこしもない|いまいちない|ぜんぜんない|そもそもない|いけない|ゼッタイない|今ひとつない|今一つもない|行けない|あまりない|なくていい|なくても?OK|なくても?結構|少しもない|今一つない|今いちない|言えるない|いえるない|行かん|あかん|いかん|なくても?良い|てはだめ|[ちじ]ゃだめ|余りない|絶対ない|全くない|今一ない|全然ない|もんか|ものか|あるますん|ない|いない|思うない|思えるない|訳[がではもじゃ]*ない|わけ[がではもじゃ]?ない'
CVS_TABLE = {
    'suki': ['iya'],
    'ikari': ['yasu'],
    'kowa': ['yasu'],
    'yasu': ['ikari', 'takaburi', 'odoroki', 'haji', 'kowa'],
    'iya': ['yorokobi', 'suki'],
    'aware': ['suki', 'yorokobi', 'takaburi', 'odoroki', 'haji'],
    'takaburi': ['yasu', 'aware'],
    'odoroki': ['yasu', 'aware'],
    'haji': ['yasu', 'aware'],
    'yorokobi': ['iya']
}

# Compiling regular expression patterns
BRACKET = r'\(\（\【\{\〈\［\｛\＜\｜|'
EMOTICON_CHARS = r'￣◕´_ﾟ・｀\-^ ･＾ω`＿゜∀/Д　~дT▽oー<。°∇；ﾉ>ε)(≦;\'▼⌒*ノ─≧ゝ●□＜＼0.○━＞|Oｰ+◎｡◇艸Ｔ’зv∩x┬☆＠,\=ヘｪェｏ△／ёロへ０\"皿．3つÅ、σ～＝U\@Θ‘uc┳〃ﾛｴqＯ３∪ヽ┏エ′＋〇ρＵ‐A┓っｖ∧曲Ω∂■､\:ˇpiο⊃〓Q人口ιＡ×）―mV＊ﾍ\?эｑ（，P┰πδｗｐ★I┯ｃ≡⊂∋L炎Зｕｍｉ⊥◆゛w益一│ожбμΦΔ→ゞj\\\tθｘ∈∞”‥¨ﾞye\]8凵ОλメしＬ†∵←〒▲\[Y\!┛сυνΣΑうＩＣ◯∠∨↑￥♀」“〆ﾊnldbXóŐÅ癶乂工шчхнЧЦЛψΨΟΛΙヮムハテコすｙｎｌｊＶＱ√≪⊇⊆＄″♂±｜ヾ？：ﾝｮf\%òå冫冖丱个凸┗┼цпШАφτηζβαΓンワゥぁｚｒｋｄｂＸＰＨＤ８♪≫↓＆「［々仝!ﾒｼ｣'
RE_EMOTICON = re.compile(r'(['+BRACKET+'])(['+EMOTICON_CHARS+']{3,}).*')
RE_POS = re.compile(r'感動|フィラー')
RE_MIDAS = re.compile(r'^(?:て|ね)(?:え|ぇ)$')
RE_KII = re.compile(r'^aware$|^haji$|^ikari$|^iya$|^kowa$|^odoroki$|^suki$|^takaburi$|^yasu$|^yorokobi$')
RE_VALANCE_POS = re.compile(r'yasu|yorokobi|suki')
RE_VALANCE_NEG = re.compile(r'iya|aware|ikari|kowa')
RE_VALANCE_NEU = re.compile(r'takaburi|odoroki|haji')
RE_ACTIVATION_A = re.compile(r'takaburi|odoroki|haji|ikari|kowa')
RE_ACTIVATION_P = re.compile(r'yasu|aware')
RE_ACTIVATION_N = re.compile(r'iya|yorokobi|suki')


class MLAsk(object):

    def __init__(self, mecab_arg=''):
        """Initialize MLAsk.

        Parameters
        ----------
        mecab_arg : str
            Argument parameters for MeCab.

        Examples
        --------
        >>> import mlask
        >>> mlask.MLAsk('-d /usr/local/lib/mecab/dic/ipadic')  #doctest: +ELLIPSIS
        <mlask.MLAsk object at 0x...>
        """
  
        self.mecab = MeCaB.Tagger(dictionary="unidic-lite")
        self._read_emodic()

        self.mecab.parse('')

    def _read_emodic(self):
        """ Load emotion dictionaries """

        self.emodic = {'emotem': {}, 'emotion': {}}

        # Reading dictionaries of syntactical indicators of emotiveness
        emotemy = ('interjections', 'exclamation', 'vulgar', 'endearments', 'emotikony', 'gitaigo')
        for emotem_class in emotemy:
            file = f"{emotem_class}_uncoded.txt"
            emotions_dir = Path(os.path.dirname(os.path.abspath(__file__))) / "emotemes"
            file_path = emotions_dir / file

            data = file_path.read_text(encoding='utf8')

            phrases = data.splitlines()
            self.emodic['emotem'][emotem_class] = phrases

        # Reading dictionaries of emotion
        emotions = ('aware', 'haji', 'ikari', 'iya', 'kowa', 'odoroki', 'suki', 'takaburi', 'yasu', 'yorokobi')
        for emotion_class in emotions:
            file = f"{emotion_class}_uncoded.txt"
            emotions_dir = Path(os.path.dirname(os.path.abspath(__file__))) / "emotions"
            file_path = emotions_dir / file

            data = file_path.read_text(encoding='utf8')

            phrases = data.splitlines()
            self.emodic['emotion'][emotion_class] = phrases

    def analyze(self, text):
        """ Detect emotion from text

        Parameters
        ----------
        text: str
            Target text.

        Return
        ------
        dict
            Result of emotion analysis.

        Examples
        --------
        >>> import mlask
        >>> ma = mlask.MLAsk()
        >>> ma.analyze('彼女のことが嫌いではない！(;´Д`)')
        {'text': '彼女のことが嫌いではない！(;´Д`)', 'emotion': defaultdict(<class 'list'>, {'yorokobi': ['嫌い*CVS'], 'suki': ['嫌い*CVS']}), 'orientation': 'POSITIVE', 'activation': 'NEUTRAL', 'emoticon': ['(;´Д`)'], 'intension': 2, 'intensifier': {'exclamation': ['！'], 'emotikony': ['´Д`', 'Д`', '´Д', '(;´Д`)']}, 'representative': ('yorokobi', ['嫌い*CVS'])}
        """
        # Normalizing
        text = self._normalize(text)

        # Lemmatization by MeCab
        lemmas = self._lexical_analysis(text)

        # Finding emoticon
        emoticon = self._find_emoticon(text)

        # Finding intensifiers of emotiveness
        intensifier = self._find_emotem(lemmas, emoticon)
        intension = len(list(intensifier.values()))

        # Finding emotional words
        emotions = self._find_emotion(lemmas)

        # Estimating sentiment orientation {POSITIVE, NEUTRAL, NEGATIVE}
        orientation = self._estimate_sentiment_orientation(emotions)

        # Estimating activeness {ACTIVE, NEUTRAL, PASSIVE}
        activation = self._estimate_activation(emotions)

        if emotions:
            result = {
                'text': text,
                'emotion': emotions,
                'orientation': orientation,
                'activation': activation,
                'emoticon': emoticon if emoticon else None,
                'intension': intension,
                'intensifier': intensifier,
                'representative': self._get_representative_emotion(emotions)
                }
        else:
            result = {
                'text': text,
                'emotion': None
            }
        return result

    def _normalize(self, text):
        text = text.replace('!', '！').replace('?', '？')
        return text

    def _lexical_analysis(self, text):
        """ By MeCab, doing lemmatization and finding emotive indicator """
        lemmas = {'all': '', 'interjections': [], 'no_emotem': [], 'lemma_words': []}


        for line in self.mecab.parse(text).splitlines():
            try:
                row = line.split('\t')
                if len(row) < 2:
                    continue
                surface = row[0]

                features = row[1:]

                if len(features) > 7:
                    (pos, subpos, lemma) = features[0], features[1], features[8]
                elif len(features) == 1:
                    pos = None
                    subpos = None
                    lemma = None
                else:
                    (pos, subpos, lemma) = features[0], features[1], surface
                if pos and subpos and lemma:
                    lemmas['lemma_words'].append(lemma)
                    if RE_POS.search(pos + subpos) or RE_MIDAS.search(surface):
                        lemmas['interjections'].append(surface)
                    else:
                        lemmas['no_emotem'].append(surface)
            except UnicodeDecodeError:
                pass

        lemmas['all'] = ''.join(lemmas['lemma_words']).replace('*', '')
        lemmas['no_emotem'] = ''.join(lemmas['no_emotem'])
        return lemmas

    def _find_emoticon(self, text):
        """ Finding emoticon """
        emoticons = []
        if RE_EMOTICON.search(text):
            emoticon = RE_EMOTICON.search(text).group(1) + RE_EMOTICON.search(text).group(2)
            emoticons.append(emoticon)
        return emoticons

    def _find_emotem(self, lemmas, emoticons):
        """ Finding syntactical indicator of emotiveness """
        emotemy = {}
        for (emotem_class, emotem_items) in self.emodic['emotem'].items():
            found = []
            for emotem_item in emotem_items:
                if emotem_item in lemmas['no_emotem']:
                    found.append(emotem_item)
            if emotem_class == 'emotikony':
                if len(emoticons) > 0:
                    found.append(','.join(emoticons))
            elif emotem_class == 'interjections':
                if len(lemmas['interjections']) > 0:
                    found.append(''.join(lemmas['interjections']))

            if len(found) > 0:
                found = [x for x in found if len(x) > 0]
                emotemy[emotem_class] = found
        return emotemy

    def _find_emotion(self, lemmas):
        """ Finding emotion word by dictionaries """

        # Build all sentences comprised of words from the text (max number of words = 7)
        total_length = len(lemmas['lemma_words'])
        sentences = [''.join(lemmas['lemma_words'][i:j+1]) for i in range(total_length) for j in range(i, i + 7 if i + 7 <= total_length else total_length)]
        text_sentences = set(sentences)
        found_emotions = collections.defaultdict(list)
        for emotion_class, emotions in self.emodic['emotion'].items():
            for emotion in emotions:
                if emotion not in text_sentences:
                    continue
                cvs_regex = re.compile('%s(?:%s(%s))' % (emotion, RE_PARTICLES, RE_CVS))
                # If there is Contextual Valence Shifters
                if cvs_regex.findall(lemmas['all']):
                    for new_emotion_class in CVS_TABLE[emotion_class]:
                        found_emotions[new_emotion_class].append(emotion + "*CVS")
                else:
                    found_emotions[emotion_class].append(emotion)
        return found_emotions if found_emotions else None

    def _estimate_sentiment_orientation(self, emotions):
        """ Estimating sentiment orientation (POSITIVE, NEUTRAL, NEGATIVE) """
        orientation = ''
        if emotions:
            how_many_valence = ''.join(emotions.keys())
            how_many_valence = RE_VALANCE_POS.sub('P', how_many_valence)
            how_many_valence = RE_VALANCE_NEG.sub('N', how_many_valence)
            how_many_valence = RE_VALANCE_NEU.sub('NorP', how_many_valence)
            num_positive = how_many_valence.count('P')
            num_negative = how_many_valence.count('N')
            if num_negative == num_positive:
                orientation = 'NEUTRAL'
            else:
                if num_negative > 0 and num_positive > 0:
                    orientation += 'mostly_'
                orientation += 'POSITIVE' if num_positive > num_negative else 'NEGATIVE'
            return orientation

    def _estimate_activation(self, emotions):
        """ Estimating activeness (ACTIVE, NEUTRAL, PASSIVE) """
        activation = ''
        if emotions:
            how_many_activation = ''.join(emotions.keys())
            how_many_activation = RE_ACTIVATION_A.sub('A', how_many_activation)
            how_many_activation = RE_ACTIVATION_P.sub('P', how_many_activation)
            how_many_activation = RE_ACTIVATION_N.sub('N', how_many_activation)
            count_activation_A = how_many_activation.count('A')
            count_activation_P = how_many_activation.count('P')

            if count_activation_A == count_activation_P:
                activation = 'NEUTRAL'
            else:
                if count_activation_A > 0 and count_activation_P > 0:
                    activation = 'mostly_'
                activation += 'ACTIVE' if count_activation_A > count_activation_P else 'PASSIVE'
            return activation

    def _get_representative_emotion(self, emotions):
        '''
        Extract emotion has most longest word from emotional words
        '''
        return sorted(emotions.items(), key=lambda x: len(x[1][0]), reverse=True)[0]
