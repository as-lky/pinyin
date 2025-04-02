import json
from math import log, isclose
from tqdm import tqdm
import sys

#pr = (zi, yin)
yin2pr = {}
id2pr = []
pr2id = {}
PREFIX = '../data'
AAA = PREFIX + '/word2pinyin.txt'
BBB = PREFIX + '/1_word.txt'
CCC = PREFIX + '/2_word.txt'
with open(AAA, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:
        line_ = line.strip()
        zi = line_[0]
        yin = line_[2:]
        id2pr.append((zi, yin))
        pr2id[(zi, yin)] = len(id2pr) - 1
        
        if yin not in yin2pr:
            yin2pr[yin] = [(zi, yin)]
        else :
            yin2pr[yin].append((zi, yin))

with open(BBB, 'r', encoding='utf-8') as f1:
    data1 = json.load(f1)

with open(CCC, 'r', encoding='utf-8') as f2:
    data2 = json.load(f2)
    

len_pr = len(id2pr)
cnt_pr = [0] * len_pr
cnt_prpr = [{} for _ in range(len_pr)]

for a, b in tqdm(data1.items()):
    for _ in range(len(b['words'])):
        pr_tmp = (b['words'][_], a)
        if pr_tmp not in pr2id:
#            print("OK")
            continue
        num_tmp = b['counts'][_]
        cnt_pr[pr2id[pr_tmp]] += num_tmp

for a, b in tqdm(data2.items()):
    for _ in range(len(b['words'])):
        tmp = b['words'][_]
        fi_zi, se_zi = tmp.split(' ', 1)
        tmp = a
        fi_yin, se_yin = tmp.split(' ', 1)
        fi_pr = (fi_zi, fi_yin)
        se_pr = (se_zi, se_yin)
        if fi_pr not in pr2id or se_pr not in pr2id:
            continue
        cnt_prpr[pr2id[fi_pr]][pr2id[se_pr]] = cnt_prpr[pr2id[fi_pr]].get(pr2id[se_pr], 0) + b['counts'][_]

cnt_yin = {}
total_cnt = 0
for _ in range(len(cnt_pr)):
    total_cnt += cnt_pr[_]
    cnt_yin[id2pr[_][1]] = cnt_yin.get(id2pr[_][1], 0) + cnt_pr[_]

assert total_cnt

#print(cnt_yin)

#print(min([_ for _ in PP if _ > 1e-12]))

def P(x, y): # P(y | x)
    xx = pr2id[x]
    yy = pr2id[y]
    lambda_ = 0.998
    A = cnt_prpr[xx].get(yy, 0)
#    print(cnt_pr[yy] / cnt_yin[y[1]])
    return ( A / cnt_pr[xx] * lambda_ if cnt_pr[xx] != 0 else 0 ) + cnt_pr[yy] / total_cnt * (1 - lambda_) # total_cnt!!!

def work(words):
    MAX = float(999999999)
    eps = float(1e-16)
    
    num = len(words)
    f = [[MAX] * len_pr, [MAX] * len_pr]
    ans = [[""] * len_pr, [""] * len_pr]
    
    ANS = ""
    QQQ = MAX
    for i in yin2pr[words[0]]:
        if cnt_pr[pr2id[i]] != 0:
            f[0][pr2id[i]] = -log(cnt_pr[pr2id[i]] / total_cnt) # the first is total_cnt! But seems same
             
        ans[0][pr2id[i]] = i[0]
        if QQQ > f[0][pr2id[i]]:
            QQQ = f[0][pr2id[i]]
            ANS = ans[0][pr2id[i]]
    
    for i in range(1, num):
        now = i & 1
        f[now] = [MAX] * len_pr
        ans[now] = [""] * len_pr
        Q = MAX
        for j in yin2pr[words[i]]:
            for k in yin2pr[words[i - 1]]:
                TT = P(k, j)
                if isclose(TT, 0, rel_tol=eps):
                    TT = eps
                if f[now][pr2id[j]] > f[now ^ 1][pr2id[k]] - log(TT):
                    f[now][pr2id[j]] = f[now ^ 1][pr2id[k]] - log(TT)
                    ans[now][pr2id[j]] = ans[now ^ 1][pr2id[k]] + j[0]
            if Q > f[now][pr2id[j]]:
                Q = f[now][pr2id[j]]
                ANS = ans[now][pr2id[j]]
    return ANS

for line in tqdm(sys.stdin):
    line_ = line.strip()
    if not line_:
        continue
    words = line_.split()
    print(work(words))
