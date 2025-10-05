from pathlib import Path

path_list_str = [
    "CoinedWord.csv",
    "EC.csv",
    "EF.csv",
    "EP.csv",
    "ETM.csv",
    "ETN.csv",
    "Foreign.csv",
    "Group.csv",
    "Hanja.csv",
    "IC.csv",
    "Inflect.csv",
    "J.csv",
    "MAG.csv",
    "MAJ.csv",
    "MM.csv",
    "NNB.csv",
    "NNBC.csv",
    "NNG.csv",
    "NNP.csv",
    "NorthKorea.csv",
    "NP.csv",
    "NR.csv",
    "Person-actor.csv",
    "Person.csv",
    "Place-address.csv",
    "Place-station.csv",
    "Place.csv",
    "Preanalysis.csv",
    "Symbol.csv",
    "VA.csv",
    "VCN.csv",
    "VCP.csv",
    "Wikipedia.csv",
    "XPN.csv",
    "XR.csv",
    "XSA.csv",
    "XSN.csv",
    "XSV.csv",
]

data = ""
for file in path_list_str:
    data +=  Path(file).read_text(encoding="utf8")

data = data.replace("\n\n", "\n")
Path("./lex.csv").write_text(data, encoding="utf-8")