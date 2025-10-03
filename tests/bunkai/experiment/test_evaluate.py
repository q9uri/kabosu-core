from kabosu_core.bunkai.constant import METACHAR_LINE_BREAK, METACHAR_SENTENCE_BOUNDARY
from kabosu_core.bunkai.experiment.evaluate import trim




def test_evaalute():
        SB = METACHAR_SENTENCE_BOUNDARY
        LB = METACHAR_LINE_BREAK
        test_cases = [
            f"yy {SB}zz", f"yy {SB}zz",
            f"yy {LB}{SB}zz", f"yy {LB}{SB}zz",
            f"yy {LB}{SB} zz", f"yy {LB} {SB}zz",
            f"yy {LB} {SB} zz", f"yy {LB}  {SB}zz",
            f"yy{SB} zz", f"yy {SB}zz",
            f"yy{SB}  zz", f"yy  {SB}zz",
            "yy zz", "yy zz",
            "yy  zz", "yy  zz",
            f"yy {LB}zz", f"yy {LB}zz",
            f"yy {LB} zz", f"yy {LB} zz",
            f"y{SB}{LB}{SB}zz", f"y{LB}{SB}zz",
        ]
        for input in test_cases:
            trimed = trim(input)
            assert input == trimed, f"input: {input}. trimed: {trimed}"

