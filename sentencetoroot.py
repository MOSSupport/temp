from neo4j import GraphDatabase
import re

def get_sentencetorootsentece(tx, sentence):
        return tx.run("""
        with $sentence as line
        with split (trim(line),' ') as words
        unwind words as word
        optional match (d:Derivative{vocab:word})--(r:RootWord)
        with word, case when d.drroot is null then r.vocab else d.drroot end as root ,case when d.drroot is null then r.tag else d.tag end as tag
        where not word = ''
        return word, replace(root, ' ', '_') as rootword, tag as roottag
        """, sentence=sentence)

def getSentencetoroot(sentence):
    # 원형기는 지정해 주어야 한다.
    #neo4j = neo4jdriver("192.168.1.211", 47687, seturi=True)
    
    with GraphDatabase.driver("bolt://192.168.1.211:47687", auth=("neo4j", "mostakeview@!")) as neo4j:
        with neo4j.session() as session:
            tx = session.begin_transaction()
            results = get_sentencetorootsentece(tx, sentence)
        
    tmp_results_words = [{'word': x['word'], 'rootword': x['rootword'], 'roottag': x['roottag']} for x in results]


    pos_str = ' '.join([s['rootword'] if s['rootword'] is not None else s['word'] for s in tmp_results_words])  # 원형만 모아보기
    pos_str_tag = ' '.join(["%s%s%s" % (s['rootword'], "/", s['roottag']) if s['rootword'] is not None else "%s%s%s" % (s['word'], "/", "NA") for s in tmp_results_words])  # 원형만 모아보기
    neo4j.close()
    return pos_str, pos_str_tag

def get_sentencetorootsentece_mm(tx, sentence):
        return tx.run("""
        with $sentence as line
        with split (trim(line),' ') as words
        unwind words as word
        optional match (d:Derivative{vocab:word})--(r:RootWord{tag:'MM'})
        with word, case when d.drroot is null then r.vocab else d.drroot end as root ,case when d.drroot is null then r.tag else d.tag end as tag
        where not word = ''
        return word, replace(root, ' ', '-') as rootword, tag as roottag
        """, sentence=sentence)

def getSentencetoroot_mm(sentence):
    # 원형기는 지정해 주어야 한다.
    #neo4j = neo4jdriver("192.168.1.211", 47687, seturi=True)
    
    with GraphDatabase.driver("bolt://192.168.1.211:47687", auth=("neo4j", "mostakeview@!")) as neo4j:
        with neo4j.session() as session:
            tx = session.begin_transaction()
            results = get_sentencetorootsentece_mm(tx, sentence)
        
    tmp_results_words = [{'word': x['word'], 'rootword': x['rootword'], 'roottag': x['roottag']} for x in results]


    pos_str = ' '.join([s['rootword'] if s['rootword'] is not None else s['word'] for s in tmp_results_words])  # 원형만 모아보기
    pos_str_tag = ' '.join(["%s%s%s" % (s['rootword'], "/", s['roottag']) if s['rootword'] is not None else "%s%s%s" % (s['word'], "/", "NA") for s in tmp_results_words])  # 원형만 모아보기
    neo4j.close()
    return pos_str, pos_str_tag


######################################
def get_sentencetorootsentece_fast(tx, sentence):
        return tx.run("""
        with $sentence as line
        with split (line,' ') as words
        unwind words as word
        optional match (d:Derivative{vocab:word})--(r:RootWord)
        return word, case when d.drroot is null then r.vocab else d.drroot end as rootword ,case when d.drroot is null then r.tag else d.tag end as roottag, id(d) as wordid, id(r) as rootid
        """, sentence=sentence)

def alphatotoken(word):
    
    # tmp_str = re.sub(r"([a-zA-Z]+)", r"<\g<0>>", str)
    tmp_str = re.sub(r"([^가-힣]+)", r"\g<0>", word)
    alpha = {'a':'에이', 'b':'비', 'c': '씨', 'd': '디', 'e': '이', 'f': '에프', 'g': '지', 'h': '에이치', 'i': '아이', 'j': '제이', 
            'k': '케이', 'l': '엘', 'm': '엠', 'n': '엔', 'o': '오', 'p': '피', 'q': '큐', 'r': '알', 's': '에스', 't': '티', 'u': '유',
            'v': '브이', 'w': '더블유', 'x': '엑스', 'y': '와이', 'z': '젯', 
            'A':'에이', 'B':'비', 'C': '씨', 'D': '디', 'E': '이', 'F': '에프', 'G': '지', 'H': '에이치', 'I': '아이', 'J': '제이', 
            'K': '케이', 'L': '엘', 'M': '엠', 'N': '엔', 'O': '오', 'P': '피', 'Q': '큐', 'R': '알', 'S': '에스', 'T': '티', 'U': '유',
            'V': '브이', 'W': '더블유', 'X': '엑스', 'Y': '와이', 'Z': '젯',}
    tmp = list()
    for w in tmp_str:
        if w in alpha:
            tmp.append(alpha[w])
        else:
            tmp.append(w)
        
    return ''.join(tmp)

def get_wordtoroot(tx, word):
        return tx.run("""
        with $word as word
        optional match (d:Derivative{vocab:word})--(r:RootWord)
        with word, case when d.drroot is null then r.vocab else d.drroot end as root ,case when d.drroot is null then r.tag else d.tag end as tag
        where not word = ''
        return word, root as rootword, tag as roottag
        """, word=word)

def getSentencetoroot_slow(sentence):
    # 원형기는 지정해 주어야 한다.
    #neo4j = neo4jdriver("192.168.1.211", 47687, seturi=True)

    words = str(sentence).strip().split()
    words_dict = dict()
    words_pos_str = []
    words_pos_str_tag = []

    with GraphDatabase.driver("bolt://192.168.1.211:47687", auth=("neo4j", "mostakeview@!")) as neo4j:
        with neo4j.session() as session:
            word_index = 0
            for word in words:
                kor_word = alphatotoken(word)
                results = session.read_transaction(get_wordtoroot, kor_word)

                tmp_results_words = [{'word': x['word'], 'rootword': x['rootword'], 'roottag': x['roottag']} for x in results]
                rootwords = [s['rootword'] if s['rootword'] is not None else word for s in tmp_results_words]
                word_pos_str = ' '.join(rootwords)
                for rootword in rootwords:
                    index = words_dict.get(rootword, -1)
                    if index < 0:
                        words_dict.update({rootword : word_index})
                word_pos_str_tag = ' '.join(["%s%s%s%s%d" % (s['rootword'], "/", s['roottag'], "/", words_dict.get(s['rootword'])) if s['rootword'] is not None else "%s%s%s%s%d" % (word, "/", "NA", "/", words_dict.get(word)) for s in tmp_results_words])  # 원형만 모아보기
                words_pos_str.append(word_pos_str)
                words_pos_str_tag.append(word_pos_str_tag)
                word_index += 1

    pos_str = ' '.join(words_pos_str)
    pos_str_tag = ' '.join(words_pos_str_tag)
    return pos_str, pos_str_tag

def getSentencetoroot_fast(sentence):
    # 원형기는 지정해 주어야 한다.
    #neo4j = neo4jdriver("192.168.1.211", 47687, seturi=True)
    kor_words = []
    words = str(sentence).split()
    if len(words) == 0: return ("", "")
    for word in words:
        kor_words.append(alphatotoken(word))
    kor_sentence = ' '.join(kor_words)
    with GraphDatabase.driver("bolt://192.168.1.211:47687", auth=("neo4j", "mostakeview@!")) as neo4j:
        with neo4j.session() as session:
            tx = session.begin_transaction()
            results = get_sentencetorootsentece_fast(tx, kor_sentence)

    tmp_results_words = [{'word': x['word'], 'wordid': x['wordid'], 'rootid': x['rootid'], 'rootword': x['rootword'], 'roottag': x['roottag']} for x in results]


    #pos_str = ' '.join([s['rootword'] if s['rootword'] is not None else s['word'] for s in tmp_results_words])  # 원형만 모아보기

    sentence_index = -1 # 입력 문장의 index
    last_word = None
    last_wordid = None
    last_rootid = None
    last_root = None
    last_root_tag = None
    words_dict = dict()
    for tmp_results_word in tmp_results_words:
        current_word = tmp_results_word.get('word')
        current_wordid = tmp_results_word.get('wordid')
        current_rootid = tmp_results_word.get('rootid')
        current_root = tmp_results_word.get('rootword')
        current_root_tag = tmp_results_word.get('roottag')
        if current_word == last_word:
            if current_rootid == last_rootid and current_wordid == last_wordid:
                sentence_index = sentence_index +1
        else:
            sentence_index = sentence_index +1
        
        #if current_word == "며" or current_word == "임하겠다":
        #gmcui print(current_word + ":::" + str(sentence_index) + ":::::" + words[sentence_index])
        #print(words[sentence_index])
        if current_root is None:
            dict_word = words[sentence_index]
        else:
            dict_word = current_root

        index = words_dict.get(dict_word, -1)
        if index < 0:
            words_dict.update({dict_word : sentence_index})

        tmp_results_word.update({'index': words_dict.get(dict_word)})
        tmp_results_word.update({'dict_word': dict_word})

        last_word = current_word
        last_wordid = current_wordid
        last_rootid = current_rootid
        last_root = current_root
        last_root_tag = current_root_tag

    pos_str = ' '.join([s['dict_word'] for s in tmp_results_words])  # 원형만 모아보기
    pos_str_tag = ' '.join(["%s%s%s%s%d" % (s['rootword'], "/", s['roottag'], "/", s['index']) if s['rootword'] is not None else "%s%s%s%s%d" % (s['dict_word'], "/", "NA", "/", s['index']) for s in tmp_results_words]) # 원형만 모아보기
    neo4j.close()
    return pos_str, pos_str_tag

def getSentencetoroot_org(sentence):
    # 원형기는 지정해 주어야 한다.
    #neo4j = neo4jdriver("192.168.1.211", 47687, seturi=True)
    kor_words = []
    words = str(sentence).split()
    if len(words) == 0: return ("", "")
    for word in words:
        kor_words.append(alphatotoken(word))
    kor_sentence = ' '.join(kor_words)
    with GraphDatabase.driver("bolt://192.168.1.211:47687", auth=("neo4j", "mostakeview@!")) as neo4j:
        with neo4j.session() as session:
            tx = session.begin_transaction()
            results = get_sentencetorootsentece_fast(tx, kor_sentence)

    tmp_results_words = [{'word': x['word'], 'wordid': x['wordid'], 'rootid': x['rootid'], 'rootword': x['rootword'], 'roottag': x['roottag']} for x in results]


    #pos_str = ' '.join([s['rootword'] if s['rootword'] is not None else s['word'] for s in tmp_results_words])  # 원형만 모아보기

    sentence_index = -1 # 입력 문장의 index
    last_word = None
    last_wordid = None
    last_rootid = None
    last_root = None
    last_root_tag = None
    words_dict = dict()
    for tmp_results_word in tmp_results_words:
        current_word = tmp_results_word.get('word')
        current_wordid = tmp_results_word.get('wordid')
        current_rootid = tmp_results_word.get('rootid')
        current_root = tmp_results_word.get('rootword')
        current_root_tag = tmp_results_word.get('roottag')
        if current_word == last_word:
            if current_rootid == last_rootid and current_wordid == last_wordid:
                sentence_index = sentence_index +1
        else:
            sentence_index = sentence_index +1
        
        #if current_word == "며" or current_word == "임하겠다":
        #gmcui print(current_word + ":::" + str(sentence_index) + ":::::" + words[sentence_index])
        #print(words[sentence_index])
        if current_root is None:
            dict_word = words[sentence_index]
        else:
            dict_word = current_root

        index = words_dict.get(dict_word, -1)
        if index < 0:
            words_dict.update({dict_word : sentence_index})

        tmp_results_word.update({'index': words_dict.get(dict_word)})
        tmp_results_word.update({'dict_word': dict_word})

        last_word = current_word
        last_wordid = current_wordid
        last_rootid = current_rootid
        last_root = current_root
        last_root_tag = current_root_tag

    pos_str = ' '.join([s['dict_word'] for s in tmp_results_words])  # 원형만 모아보기
    pos_str_tag = ' '.join(["%s%s%s%s%d" % (s['rootword'], "/", s['roottag'], "/", s['index']) if s['rootword'] is not None else "%s%s%s%s%d" % (s['dict_word'], "/", "NA", "/", s['index']) for s in tmp_results_words]) # 원형만 모아보기
    neo4j.close()
    return pos_str, pos_str_tag
