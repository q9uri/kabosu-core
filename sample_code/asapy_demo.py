#50 line
GET_RESULT_JSON_USES = """
================================================== 
|
| from kabosu_core.asapy import ASA
|
| asa = ASA()
|
| asa.parse("太郎は6時に次郎を追いかけた。")
|
| print(asa.get_result_json())
|
|
| print to result ↓
================================================== 
"""


#50 line
GET_RESULT_USES = """
================================================== 
|
| from kabosu_core.asapy import ASA
|
| asa = ASA()
|
| asa.parse("太郎は6時に次郎を追いかけた。")
|
| asa.get_result()
|
|
| print to result ↓
================================================== 
"""


from kabosu_core.asapy import ASA
import time

asa = ASA()

asa.parse("太郎は6時に次郎を追いかけた。")

print(GET_RESULT_JSON_USES)
print("demo stopping to 10s (for reads)")
time.sleep(10)
asa.get_result()

print(GET_RESULT_JSON_USES)
print("demo stopping to 10s (for reads)")
time.sleep(10)
print(asa.get_result_json()) 