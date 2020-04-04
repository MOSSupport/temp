# -*- coding: utf-8 -*-
# 2019 05 15 AsiaToday용
import re
import sys


# https://stackoverflow.com/questions/42070323/split-on-spaces-not-inside-parentheses-in-python
def parenthesis_split(sentence, separator=" ", lparen="(", rparen=")"):
    nb_brackets = 0
    sentence = sentence.strip(separator)  # get rid of leading/trailing seps

    l = [0]
    for i, c in enumerate(sentence):
        if c == lparen:
            nb_brackets += 1
        elif c == rparen:
            nb_brackets -= 1
        elif c == separator and nb_brackets == 0:
            l.append(i)
        # handle malformed string
        if nb_brackets < 0:
            raise Exception("Syntax error")

    l.append(len(sentence))
    # handle missing closing parentheses
    if nb_brackets > 0:
        raise Exception("Syntax error")

    return ([sentence[i:j].strip(separator) for i, j in zip(l, l[1:])])


def replace_parentheses_sentence(sentence):
    # 괄호 공백구문을 뒤로 보내기 쉽게 하기 위해서 중간에 공백이 있는 것들은 찾아서 합치자. 나중에 정규식 잘하면 다시 생각해 보자. 인터넷에 보니 괄호를 남기면서 나누는게 있더라.

    # for m in [x for x in re.findall('\(.*?\)', sentence)]:
    #     sentence = (re.sub(re.escape(m), re.sub(" ", "", m), sentence))
    # split_sentence = sentence.split() # 위에 붙인 다음에 이걸 해야 한다.

    # 20190114 추가 : 괄호가 시작이 없거나 하는것도 있다. 예외처리 필요
    try:
        split_sentence = parenthesis_split(sentence)
    except:
        split_sentence = sentence.split()

    # 중간의 괄호문자를 뒤로 보내보자
    replace_parentheses = []
    for m in split_sentence:
        match = (re.search('(\(.*\))', m))  # 괄호 문자를 찾는다.

        if match:
            remove_parentheses = re.sub('\(|\)', '', match.group())  # 치환하기 위해서 내용만 추출한다.
            replace_parentheses.append([re.sub(re.escape(match.group()), "", m)])  # 1차로 본문에서 괄호를 삭제한다.
            # https://hashcode.co.kr/questions/493/%EC%97%AC%EB%9F%AC%EA%B0%9C-%EB%AC%B8%EC%9E%90%EB%A5%BC-%EA%B8%B0%EC%A4%80%EC%9C%BC%EB%A1%9C-%EB%AC%B8%EC%9E%90%EC%97%B4%EC%9D%84-%EC%9E%90%EB%A5%B4%EB%8A%94-%EB%B0%A9%EB%B2%95%EC%9D%B4-%EC%9E%88%EB%82%98%EC%9A%94
            replace_parentheses.append(remove_parentheses.replace(',', ' ').split())  # 삭제 후 뒤 list에 붙여준다.
        else:
            replace_parentheses.append([m])  # 일반 문장은 순서대로 붙인다..
    return ' '.join([item for sublist in replace_parentheses for item in sublist])


def getPreprocessingSent(sentence):
    """
    원형기용 전처리
    """
    try:
        # 주 -> 주식회사 치환.
        resultstring = re.sub('\(주\)|㈜', "주식회사", sentence)
        # 사 -> 사단법인 치환.
        resultstring = re.sub('\(사\)', "사단법인 ", resultstring)
        # ./글자 -> / 삭제
        resultstring = re.sub(r'\.\/([가-힣])', r". \1", resultstring)
        # 글자 사이에 '』 가 있으면 삭제하면서 두 글자를 붙임
        resultstring = re.sub(r"([가-힣])[’'』]([가-힣])", r"\1\2", resultstring)
        # 숫자가 아니고 ,뒤에 숫자와글자가 있으면 띄움
        resultstring = re.sub(r"([^\d],)(\d+[^\d]+)", r"\1 \2", resultstring)
        # (한자) 는 삭제. 원형기에서 필요없음 https://www.epubguide.net/118
        resultstring = re.sub(r"(\([一-龥豈-龎\s]+\))", r"", resultstring)
        # 중간의 공백을 해당 문장의 뒤로 보내는 구문
        resultstring = replace_parentheses_sentence(resultstring)
        # 글자 사이에 )가 있으면 삭제하면서 두 글자를 붙임
        resultstring = re.sub(r"([A-Z가-힣])\)([가-힣])", r"\1\2", resultstring)

        # 한글영문숫자 기호 남기고 삭제 - 이게 기존에 있던거랑 비슷한거다.
        resultstring = re.sub(r"[^가-힣a-zA-Z0-9,$@&\.\- ]", r" ", resultstring)

        # 영문, 에서 , 삭제
        resultstring = re.sub(r"([A-Za-z]),", r"\1", resultstring)
        # 한글,한글 에서 , 삭제
        resultstring = re.sub(r"([가-힣]),([가-힣])?", r"\1 \2", resultstring)
        # 한글.영문숫자한글 에서 뒤에 . 삭제
        resultstring = re.sub(r"([가-힣])\.([A-Z0-9가-힣])?", r"\1 \2", resultstring)
        # 기타 이유로 덩그러니 . , - 만 남으면 삭제
        resultstring = re.sub(r"\s[\.,-]+\s", r" ", resultstring)
        # 한글.영문숫자한글 에서 뒤에 . 삭제
        resultstring = re.sub(r"\s?[\.,\-]([가-힣])", r" \1", resultstring)
        # 한글 뒤에 . , - 등이 있으면 삭제
        resultstring = re.sub(r"([가-힣])[\.,\-]\s", r" \1", resultstring)
        # 공백이 2자리 이상이면 한자리로 변경
        resultstring = re.sub(r"\s{2,}", r" ", resultstring)
    except Exception as e:
        resultstring = 'error'
    return resultstring


if __name__ == "__main__":
    if (len(sys.argv)) > 1:
        sentence = sys.argv[1]
        print("원문 : {}\n\n".format(sentence))
        print(news_remove_sentences(sentence))
    else:
        sentence = """
        아시아투데이 맹성규·김지환·조준혁 기자 = ‘황금돼지의 해’ 2019년 기해년(己亥年) 시작을 알리는 제야의 종소리를 듣기위해 서울 종로구 보신각 인근에는 시민들의 발걸음이 이어졌다. 보신각 주변은 31일 오후 8시께로부터 묵은 한 해를 보내고 희망찬 새해를 맞이하기 위해 시민들로 인산인해를 이뤘다. 청계천에는 HAPPY NEW YEAR·사슴·별·나팔부르는 소녀 모양 등 LED를 활용한 각양각색의 화려한 불빛보형물들이 수놓고 있었다. 커피, 밤, 닭꼬치, 솜사탕, 군고구마 등을 손에 쥔 시민들은 이날만큼은 근심 걱정거리를 날리려는 듯 즐거운 표정으로 만끽했다. 특히, 청계천 인근에 나온 시민들은 머리띠를 비롯해 장갑, 목도리, 귀마개 등 한파에 대비한 모습을 보였다. 아울러 ‘소원등’을 만드는 부스에는 수많은 시민들이 긴 줄을 서 기다리고 있었다. 가족들과 함께 방문한 이신우씨(43)는 “올해 마지막 날인 31일 연말을 맞이해 청계천에서 ‘소원등’을 만드는 곳에 방문했다”면서 “오늘 이렇게 ‘소원등’에 올해동안 이루지 못했던 소원들을 적어서 내년에는 다 이룰 수 있도록 가족들하고 기원해보려고 한다”고 말했다. 포장마차 앞에서 만난 전병훈씨(30)는 올해 아쉬움 점에 대해 “동네에서 옷가게를 하고 있는데 (올해) 기대한 만큼 성과가 나오지 못했다”면서 “인스타에 올려보기도 하고, 잡지도 많이 공부하면서 장사에 임했는데 성과가 별로 나오지 못해 내년에는 장사가 잘 되길 바란다”고 말했다. 부인과 함께 방문한 이정민씨(33)는 “결혼한 지 꽤 됐는데 아직 아이기 없어서 아쉬웠다”면서 “내년에는 새로운 가족을 맞이하고 싶다”고 말했다. 취업준비생 이창현씨(26)는 “하반기에 건설사 한 10군데 정도 지원했는데 떨어졌다. 친구들이 합격하는 모습을 보고 많이 ‘나는 왜 안됐을까’ 라는 생각하면서 자괴감에 빠지기도 했다”면서 “이 곳에서 ‘소원등’도 만들고 예쁜 볼거리들을 구경하니 내년을 준비할 힘이 생기는 것 같다”고 말했다. 서울시는 이날 오후 11시부터 내년 1월 1일 오전 1시30분까지 종로, 우정국로, 청계천로 등 주변 도로의 차량 진입을 통제한다. 서울시는 시민들의 교통편의를 위해 지하철을 새벽 2시(종착역 기준)까지 연장해 총 115회 증회 운행한다. 아울러 주변을 지나는 시내버스 40개 노선도 보신각 인근 정류소에서 차고지 방향으로 새벽 2시 전후로 출발한다.한편, 경찰은 제야의 종 타종 행사 현장에서 폭죽을 터뜨리면 경범죄 처벌법에 따라 처벌될 수 있다고 경고했다. 경찰 관계자는 “많은 사람이 모인 곳에서 폭죽을 사용하면 다른 사람이 다칠 수 있다며 폭죽 사용을 자제해 달라”고 당부했다.
        """
        print("원문 : {}\n\n".format(sentence))
        print(getPreprocessingSent(sentence))
