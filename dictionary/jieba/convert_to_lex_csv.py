from pathlib import Path

data = Path("./dict.txt").read_text(encoding="utf8")

out = []
for line in data.split("\n"):
    if line != "":
        split_line = line.split(" ")
        surface = split_line[0]
        cost = split_line[1]
        pos = split_line[2]

        out_line = f"{surface},{cost},0,0,{pos}"
        out.append(out_line)

Path("./lex.csv").write_text("\n".join(out), encoding="utf8")