import json
from pypinyin import lazy_pinyin
from tqdm import tqdm

A = []
B = []
C = {}

with open('../data/拼音汉字表.txt', 'r', encoding='gbk') as f:
    for line in tqdm(f.readlines()):
        line_ = line.strip()
        ww = line_.split(' ')
        for j in range(1, len(ww)):
            if ww[j] not in B:
                B.append(ww[j])
                C[ww[j]] = 1
            A.append((ww[j], ww[0]))
            
with open('../data/word2pinyin.txt', 'w', encoding='utf-8') as f:
    for i in A:
        f.write(i[0] + ' ' + i[1] + '\n')

pr_cnt = {}
prpr_cnt = {}
prprpr_cnt = {}
prprprpr_cnt = {}
head_cnt = {}
tail_cnt = {}


def add3(a, b, c):
    yin = a[1] + ' ' + b[1] + ' ' + c[1]
    zi = a[0] + b[0] + c[0]
    if yin not in prprpr_cnt:
        prprpr_cnt[yin] = {"words": [zi], "counts": [1]}
    else:
        if zi not in prprpr_cnt[yin]["words"]:
            prprpr_cnt[yin]["words"].append(zi)
            prprpr_cnt[yin]["counts"].append(1)
        else:
            prprpr_cnt[yin]["counts"][prprpr_cnt[yin]["words"].index(zi)] += 1
def add4(a, b, c, d):
    yin = a[1] + ' ' + b[1] + ' ' + c[1] + ' ' + d[1]
    zi = a[0] + b[0] + c[0] + d[0]
    if yin not in prprprpr_cnt:
        prprprpr_cnt[yin] = {"words": [zi], "counts": [1]}
    else:
        if zi not in prprprpr_cnt[yin]["words"]:
            prprprpr_cnt[yin]["words"].append(zi)
            prprprpr_cnt[yin]["counts"].append(1)
        else:
            prprprpr_cnt[yin]["counts"][prprprpr_cnt[yin]["words"].index(zi)] += 1


def add(content): # 二元 # 添加句首标志 # 含有? # 注音
    yins = lazy_pinyin(content)
    try :
        assert(len(content) == len(yins))
    except :
        print(len(content), len(yins))
        print(content)
        print(yins)
    lastpr = None
    for i in range(len(content)):
        if yins[i] == '?':
            if lastpr != None:
                tail_cnt[lastpr] = tail_cnt.get(lastpr, 0) + 1
            lastpr = None
            continue
        nowpr = (content[i], yins[i])
        pr_cnt[nowpr] = pr_cnt.get(nowpr, 0) + 1
        if lastpr == None:
            # head!
            head_cnt[nowpr] = head_cnt.get(nowpr, 0) + 1
            lastpr = nowpr
            continue
        if lastpr in prpr_cnt:
            prpr_cnt[lastpr][nowpr] = prpr_cnt[lastpr].get(nowpr, 0) + 1
        else:
            prpr_cnt[lastpr] = {nowpr: 1}
        
        lastpr = nowpr
        
        if i >= 2 and yins[i - 2] != '?':
            add3((content[i - 2], yins[i - 2]), (content[i - 1], yins[i - 1]), (content[i], yins[i]))
        if i >= 3 and yins[i - 2] != '?' and yins[i - 3] != '?':
            add4((content[i - 3], yins[i - 3]), (content[i - 2], yins[i - 2]), (content[i - 1], yins[i - 1]), (content[i], yins[i]))
       
        
def work(content): 
    SS = ""
    for i in range(len(content)):
        if content[i] in C:
            SS += content[i]
        elif SS != "" and SS[-1] != '?':
            SS += '?'
    return SS
            
def solve(fp, lll, rrr):
    
    ALL = "?"
    sum = 0
    for line in tqdm(fp.readlines()):
        sum += 1
        if sum < lll:
            continue
        if sum > rrr:
            break
        we = json.loads(line)['html']
        we = we.strip()
        we = work(we)
        if ALL[-1] == '?':
            ALL += we
        else :
            ALL += '?' + we
        if len(ALL) >= 50000:
           if ALL[-1] != '?':
               ALL += '?'
           add(ALL)
           ALL = "?"
           
    if len(ALL) > 0:
        add(ALL)

#    print("_____________________________________________________")
    

def DEL(dic, num):
    se = []
    for a, b in dic.items():
        we = []
        for _ in range(len(b['counts'])):
            if b['counts'][_] < num:
                we.append(_)
        q = 0
        for i in we: 
            del b['words'][i - q]
            del b['counts'][i - q]
            q += 1
        if len(b['words']) == 0:
            se.append(a)

    for i in se:
        del dic[i]
        

def Solve(aaa, lll, rrr):

    with open('../corpus/sina_news_gbk/' + aaa, 'r', encoding='gbk') as f:
        solve(f, lll, rrr)
    
    dic = {}
    for pr, cnt in pr_cnt.items():
        if pr[1] in dic:
            dic[pr[1]]['words'].append(pr[0])
            dic[pr[1]]['counts'].append(cnt)
        else :
            dic[pr[1]] = {'words': [pr[0]], 'counts': [cnt]}
            
    dic = {}
    for lastpr, a in prpr_cnt.items():
        for nowpr, cnt in a.items():
            yins = lastpr[1] + ' ' + nowpr[1]
            zis = lastpr[0] + ' ' + nowpr[0]
            if yins in dic:
                dic[yins]['words'].append(zis)
                dic[yins]['counts'].append(cnt)
            else :
                dic[yins] = {'words': [zis], 'counts': [cnt]}

    
    
    for a, b in prprpr_cnt.items():
        we = []
        for _ in range(len(b['counts'])):
            if b['counts'][_] < 5:
                we.append(_)
        q = 0
        for i in we: 
            del b['words'][i - q]
            del b['counts'][i - q]
            q += 1
            
    DEL(prprpr_cnt, 5)
    DEL(prprprpr_cnt, 10)
    
Solve("2016-04.txt", 1, 120000)
Solve("2016-05.txt", 1, 120000)
Solve("2016-06.txt", 1, 120000)
Solve("2016-07.txt", 1, 120000)
Solve("2016-08.txt", 1, 120000)
Solve("2016-09.txt", 1, 120000)
Solve("2016-10.txt", 1, 120000)
Solve("2016-11.txt", 1, 120000)

p1t = "../data/1_word.txt"
p2t = "../data/2_word.txt"
p3t = "../data/3_word.txt"
p4t = "../data/4_word.txt"
p5t = "../data/ht_word.txt"

dic = {}
for pr, cnt in pr_cnt.items():
    if pr[1] in dic:
        dic[pr[1]]['words'].append(pr[0])
        dic[pr[1]]['counts'].append(cnt)
    else :
        dic[pr[1]] = {'words': [pr[0]], 'counts': [cnt]}
        
with open(p1t, 'w', encoding='utf-8') as f:
    json.dump(dic, f, ensure_ascii=False, indent=4)

dic = {}
for lastpr, a in prpr_cnt.items():
    for nowpr, cnt in a.items():
        yins = lastpr[1] + ' ' + nowpr[1]
        zis = lastpr[0] + ' ' + nowpr[0]
        if yins in dic:
            dic[yins]['words'].append(zis)
            dic[yins]['counts'].append(cnt)
        else :
            dic[yins] = {'words': [zis], 'counts': [cnt]}

with open(p2t, 'w', encoding='utf-8') as f:
    json.dump(dic, f, ensure_ascii=False, indent=4)

with open(p3t, 'w', encoding='utf-8') as f:
    json.dump(prprpr_cnt, f, ensure_ascii=False, indent=4)
        
with open(p4t, 'w', encoding='utf-8') as f:
    json.dump(prprprpr_cnt, f, ensure_ascii=False, indent=4)
    
with open(p5t, 'w', encoding='utf-8') as f:
    A = {}
    for a, b in head_cnt.items():
        A[a[0] + ' ' + a[1]] = {'head_cnt' : b, 'tail_cnt' : 0}
    for a, b in tail_cnt.items():
        if a[0] + ' ' + a[1] in A:
            A[a[0] + ' ' + a[1]]['tail_cnt'] = b
        else :
            A[a[0] + ' ' + a[1]] = {'head_cnt' : 0, 'tail_cnt' : b}
    json.dump(A, f, ensure_ascii=False, indent=4)    