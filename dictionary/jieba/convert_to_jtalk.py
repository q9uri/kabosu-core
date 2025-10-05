
from pathlib import Path
data = Path("./lex.csv").read_text(encoding="utf-8")
out = []
for line in data.split("\n"):
    split_line = line.split(",")
    surface = split_line[0]
    cost = split_line[1]
    pos = split_line[4]
    out_line = f"{surface},{cost},0,0,{pos},*,*,*,*,*,{surface},{surface},{surface},*/*,*"
    out.append(out_line)

Path("./zh-jibea-noacc.csv").write_text("\n".join(out), encoding="utf8")