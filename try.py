import json
from math import log
import sys

zi2yin = {}
yin2zi = {}
id2zi = []
zi2id = {}
with open('./word2pinyin.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:
        line_ = line.strip()
        zi = line_[0]
        yin = line_[2:]
        zi2yin[zi] = yin
        id2zi.append(zi)
        zi2id[zi] = len(id2zi) - 1
        if yin not in yin2zi:
            yin2zi[yin] = [zi]
        else :
            yin2zi[yin].append(zi)

with open('./1_word.txt', 'r', encoding='utf-8') as f1:
    data1 = json.load(f1)

with open('./2_word.txt', 'r', encoding='utf-8') as f2:
    data2 = json.load(f2)
    

len_zi = len(zi2yin)
cnt_zi = [0] * len_zi
cnt_zizi = [[0] * len_zi for _ in range(len_zi)]


for b in data1.values():
    for _ in range(len(b['words'])):
        if b['words'][_] not in zi2id:
            continue
        cnt_zi[zi2id[b['words'][_]]] += b['counts'][_]

for b in data2.values():
    for _ in range(len(b['words'])):
        tmp = b['words'][_]
        fi, se = tmp.split(' ', 1)
        cnt_zizi[zi2id[fi]][zi2id[se]] += b['counts'][_]


P = [[float(0)] * len_zi for _ in range(len_zi)] # !!!
total_cnt = 0
for _ in cnt_zi:
    total_cnt += _

assert total_cnt

PP = [_ / total_cnt for _ in cnt_zi]


lambda_ = 0.95
for i in range(len_zi):
    if cnt_zi[i] == 0:
        continue # TODO : check
    for j in range(len_zi):
        P[i][j] = cnt_zizi[i][j] / cnt_zi[i] * lambda_ + cnt_zi[j] * (1 - lambda_)   
print(P[0][1])

def work(words):
    MAX = float(999999999)
    eps = float(1e-6)
    
    num = len(words)
    f = [[MAX] * len_zi, [MAX] * len_zi]
    ans = [[""] * len_zi, [""] * len_zi]
    
    ANS = ""
    for i in yin2zi[words[0]]:
        Q = MAX
        if cnt_zi[zi2id[i]] != 0:
            f[0][zi2id[i]] = -log(PP[zi2id[i]]) # TODO: check
             
        ans[0][zi2id[i]] = i
        if Q > f[0][zi2id[i]]:
            Q = f[0][zi2id[i]]
            ANS = ans[0][zi2id[i]]
    
    for i in range(1, num):
        now = i & 1
        f[now] = [MAX] * len_zi
        ans[now] = [""] * len_zi
        Q = MAX
        for j in yin2zi[words[i]]:
            for k in yin2zi[words[i - 1]]:
                if P[zi2id[k]][zi2id[j]] < eps:
                    continue
                if f[now][zi2id[j]] > f[now ^ 1][zi2id[k]] - log(P[zi2id[k]][zi2id[j]]):
                    f[now][zi2id[j]] = f[now ^ 1][zi2id[k]] - log(P[zi2id[k]][zi2id[j]])
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
    
