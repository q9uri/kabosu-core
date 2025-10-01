# g2pk4
g2pk2 is a updated folk of [Kyubyong's g2pk](https://github.com/Kyubyong/g2pK), which hasn’t been fixed in many years.

It supports Windows, Linux, and macOS based on [harmlessman's g2pk](https://github.com/harmlessman/g2pkk)

I found onther version g2pk3
I renamed g2pk4 and merge onther version g2pk3
https://github.com/kdrkdrkdr/g2pk3

## Bug fixed
* 한국어 어문 규범 제15항 (Korean grammar rules chapter 15) https://github.com/Kyubyong/g2pK/issues/6
* Bug in rule https://github.com/Kyubyong/g2pK/pull/13
## Requirements
* python >= 3.6
* jamo
* nltk


## Installation
```
pip install gitL+https://github.com/q9uri/g2pk4
```

## How To Use
g2pk2 uses same syntaxes as g2pk.
```
>>> from g2pk2 import G2p
>>> g2p = G2p()
>>> g2p("포상은 열심히 한 아이에게만 주어지기 때문에 포상인 것입니다.")
'포상은 열심히 한 아이에게만 주어지기 때무네 포상인 거심니다.'
```
If you want more information, check [g2pk](https://github.com/Kyubyong/g2pK)

## Reference
[Kyubyong/g2pk](https://github.com/Kyubyong/g2pK)<br>
[harmlessman/g2pkk](https://github.com/harmlessman/g2pkk)<br>
[tenebo/g2pk2](https://github.com/tenebo/g2pk2)<br>
[kdrkdrkdr/g2pk3](https://github.com/kdrkdrkdr/g2pk3)<br>