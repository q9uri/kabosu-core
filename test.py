from kabosu_core.pyopenjtalk.normalizer.korean import ko2ja

text = "이봐, 센파이. 한국으로 여행하자? 현지의 맛있는 요리를 먹으면 좋겠다."

text_list = [
    "오늘 하늘은 구름 한 점 없이 맑습니다.",
    "가을이라서 그런지 바람이 차갑네요.",
    "도서관에서 새 책을 빌려 읽기 시작했어요.",
    "내일 저녁 메뉴로 무엇을 만들지 고민입니다.",
    "따뜻한 차 한 잔이 생각나는 오후예요.",
    "다음 주말에는 친구들과 여행을 가기로 했어요."
]
for text in text_list: 
    out = ko2ja(text)

    print(out)