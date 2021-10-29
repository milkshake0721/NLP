import requests
import re
import time
import os
import sys
from fuzzywuzzy import fuzz
from bs4 import BeautifulSoup

working_directory = os.path.dirname(os.path.realpath(__file__))
sys.path.append(working_directory)
testing_queries = os.path.join("queries.txt")

def replace_all(string, dic):
    for i in dic:
        string = string.replace(i, dic[i])
    return string

def del_brackets_and_content(string):  # 清除()
    string = replace_all(string, {'（': '(', '）': ')'})
    pattern = ["\\(.*?\\)"]
    for p in pattern:
        string = re.sub(u"{}".format(p), "", string)
    return string


def del_square_brackets_and_content(string):  # 清除[]
    string = replace_all(string, {'（': '(', '）': ')'})
    pattern = ["\\[.*?\\]"]
    for p in pattern:
        string = re.sub(u"{}".format(p), "", string)
    return string

def get_the_link(tag):
    url = "https://zh.wikipedia.org/wiki/"+tag
    r = requests.get(url) #將網頁資料GET下來
    soup = BeautifulSoup(r.text,"html.parser") #將網頁資料以html.parser
    sel = soup.select("div p") #取HTML標中的 <div class="title"></div> 中的<p>標籤存入sel
    sel_list = soup.select("div.mw-parser-output a")#取HTML標中的 <div class="title"></div> 中的<a>標籤存入sel_list

    return sel,sel_list 

def replace_to_blank(string, replace_list):
    for token in replace_list:
        string = string.replace(token, '')
    return string

def check_numb(sel,result):
    i=0
    while(True):         #略過字數太少的框
        info = sel[i]
        if len(sel[i])>=2:
            while(fuzz.partial_ratio(sel[i],result) < 40):
                i +=1
                info = sel[i]
                if i > 3:
                    break
            break    
        i +=1
    return info


def wiki_gogo_go(result):
    tag = result

    sel = get_the_link(tag)[0]
    sel_list = get_the_link(tag)[1]
    info = check_numb(sel,result)

    if(fuzz.partial_ratio(info,'可以指') == 100):
        i=0
        new_tag = (sel_list[0]["href"][6:])
        sel = get_the_link(new_tag)[0]
        info = check_numb(sel,result)

    a = info.text
    a = del_brackets_and_content(a)
    a = del_square_brackets_and_content(a)
    b = list(a)
    c = len(b)
    k=0
    for i in range(c):
        k+=1
        if k >25:
            if b[i] == '。':
                b = b[:i+1]
                break

    content='%s'*len(b) % tuple(b)

    if (fuzz.partial_ratio(content,'维基百科目前还没有与上述标题相同的条目。') == 100):
        content = 'N/A'
    
    result = content
    result = replace_to_blank(result, ['\n', '\u200b', '\xa0'])
    return result

queries = [line.strip() for line in open(testing_queries, encoding='utf-8').readlines()]
f_result = open('result.txt', 'w', encoding='utf-8')
f_source = open('source.txt', 'w', encoding='utf-8')


for _query in queries:
    s = time.time()
    _result_json = wiki_gogo_go(_query)
    _response = _result_json
    _source = _query
    print("===" * 10)
    print(_result_json)
    f_result.write(_response)
    f_source.write(_source)
    f_result.write('\n')
    f_source.write('\n')

f_result.close()
f_source.close()