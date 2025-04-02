import json
from math import log, isclose
import sys

yin2zi = {}
id2zi = []
zi2id = {}
PREFIX = '.'
AAA = PREFIX + '/word2pinyin.txt'
BBB = PREFIX + '/1_word.txt'
CCC = PREFIX + '/2_word.txt'
with open(AAA, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:
        line_ = line.strip()
        zi = line_[0]
        yin = line_[2:]
        
        if zi not in zi2id:
            id2zi.append(zi)
            zi2id[zi] = len(id2zi) - 1
        
        if yin not in yin2zi:
            yin2zi[yin] = [zi]
        else :
            yin2zi[yin].append(zi)

with open(BBB, 'r', encoding='utf-8') as f1:
    data1 = json.load(f1)

with open(CCC, 'r', encoding='utf-8') as f2:
    data2 = json.load(f2)
    

len_zi = len(id2zi)
cnt_zi = [0] * len_zi
cnt_zi_yin = [{} for _ in range(len_zi)]
cnt_zizi = [{} for _ in range(len_zi)]

for a, b in data1.items():
    for _ in range(len(b['words'])):
        cnt_zi[zi2id[b['words'][_]]] += b['counts'][_]
        cnt_zi_yin[zi2id[b['words'][_]]][a] = cnt_zi_yin[zi2id[b['words'][_]]].get(a, 0) + b['counts'][_]

for b in data2.values():
    for _ in range(len(b['words'])):
        tmp = b['words'][_]
        fi, se = tmp.split(' ', 1)
        if zi2id[se] not in cnt_zizi[zi2id[fi]]:
            cnt_zizi[zi2id[fi]][zi2id[se]] = b['counts'][_]
        else :
            cnt_zizi[zi2id[fi]][zi2id[se]] += b['counts'][_]

total_cnt = 0
for _ in cnt_zi:
    total_cnt += _

assert total_cnt

#print(min([_ for _ in PP if _ > 1e-12]))

def P(x, x_yin, y, y_yin): # P(y | x)
    lambda_ = 0.998
    A = 0
    if y in cnt_zizi[x]:
        A = cnt_zizi[x][y] # 认为两个字不可能同时
    return ( A / cnt_zi[x] * lambda_ if cnt_zi[x] != 0 else 0 ) + PP[y] * (1 - lambda_)

def work(words):
    MAX = float(999999999)
    eps = float(1e-16)
    
    num = len(words)
    f = [[MAX] * len_zi, [MAX] * len_zi]
    ans = [[""] * len_zi, [""] * len_zi]
    
    ANS = ""
    QQQ = MAX
    for i in yin2zi[words[0]]:
        if cnt_zi[zi2id[i]] != 0:
            f[0][zi2id[i]] = -log(PP[zi2id[i]]) # TODO: check
             
        ans[0][zi2id[i]] = i
        if QQQ > f[0][zi2id[i]]:
            QQQ = f[0][zi2id[i]]
            ANS = ans[0][zi2id[i]]
    
    for i in range(1, num):
        now = i & 1
        f[now] = [MAX] * len_zi
        ans[now] = [""] * len_zi
        Q = MAX
        for j in yin2zi[words[i]]:
            for k in yin2zi[words[i - 1]]:
                TT = P(zi2id[k], zi2id[j])
                if isclose(TT, 0, rel_tol=eps):
                    TT = eps
                if f[now][zi2id[j]] > f[now ^ 1][zi2id[k]] - log(TT):
                    f[now][zi2id[j]] = f[now ^ 1][zi2id[k]] - log(TT)
                    ans[now][zi2id[j]] = ans[now ^ 1][zi2id[k]] + j
            if Q > f[now][zi2id[j]]:
                Q = f[now][zi2id[j]]
                ANS = ans[now][zi2id[j]]
    return ANS

for line in sys.stdin:
    line_ = line.strip()
    if not line_:
        continue
    words = line_.split()
    print(work(words))
