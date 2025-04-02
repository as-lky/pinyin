import json
from math import log, isclose
from tqdm import tqdm
import sys

# pr = (zi, yin)

yin2pr = {}
id2pr = []
pr2id = {}
PREFIX = '.'
AAA = PREFIX + '/word2pinyin.txt'
BBB = PREFIX + '/1_word.txt'
CCC = PREFIX + '/2_word.txt'
DDD = PREFIX + '/3_word.txt'
EEE = PREFIX + '/4_word.txt'

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

with open(DDD, 'r', encoding='utf-8') as f3:
    data3 = json.load(f3)
    
with open(EEE, 'r', encoding='utf-8') as f4:
    data4 = json.load(f4)

len_pr = len(id2pr)
cnt_pr = [0] * len_pr

for a, b in tqdm(data1.items()):
    for _ in range(len(b['words'])):
        pr_tmp = (b['words'][_], a)
        if pr_tmp not in pr2id:
            continue
        num_tmp = b['counts'][_]
        cnt_pr[pr2id[pr_tmp]] += num_tmp

total_cnt = 0
for _ in range(len(cnt_pr)):
    total_cnt += cnt_pr[_]
assert total_cnt

DIC = {}
for a, b in tqdm(data2.items()):
    for _ in range(len(b['words'])):
        strr = b['words'][_] + a
        DIC[strr] = b['counts'][_]

for a, b in tqdm(data3.items()):
    for _ in range(len(b['words'])):
        strr = b['words'][_] + a
        DIC[strr] = b['counts'][_]

for a, b in tqdm(data4.items()):
    for _ in range(len(b['words'])):
        strr = b['words'][_] + a
        DIC[strr] = b['counts'][_]
        

def get_cnt2(x, y): # cnt(x, y)
    strr = x[0] + ' ' + y[0] + x[1] + ' ' + y[1]
    return DIC.get(strr, 0)
    # w = data2.get(x[1] + ' ' + y[1], 0)
    # if w == 0:
    #     return 0
    # try:
    #     a = w['words'].index(x[0] + ' ' + y[0])
    #     return w['counts'][a]
    # except:
    #     return 0

def get_cnt3(x, y, z): # cnt(x, y, z)
    strr = x[0] + y[0] + z[0] + x[1] + ' ' + y[1] + ' ' + z[1]
    return DIC.get(strr, 0)
    # w = data3.get(x[1] + ' ' + y[1] + ' ' + z[1], 0)
    # if w == 0:
    #     return 0
    # try:
    #     a = w['words'].index(x[0] + y[0] + z[0])
    #     return w['counts'][a]
    # except:
    #     return 0

def get_cnt4(x, y, z, s): # cnt(x, y, z, s)
    strr = x[0] + y[0] + z[0] + s[0] +  x[1] + ' ' + y[1] + ' ' + z[1] + ' ' + s[1]
    return DIC.get(strr, 0)
    # w = data3.get(x[1] + ' ' + y[1] + ' ' + z[1] + ' ' + s[1], 0)
    # if w == 0:
    #     return 0
    # try:
    #     a = w['words'].index(x[0] + y[0] + z[0] + s[0])
    #     return w['counts'][a]
    # except:
    #     return 0

def P(x, y, z, w): # P(w | x,y,z)
    zz = pr2id[z]
    ww = pr2id[w]
    A = get_cnt4(x, y, z, w)
    B = get_cnt3(x, y, z)
    s1 = A / B if B != 0 else 0
    
    A = get_cnt3(y, z, w)
    B = get_cnt2(y, z)
    s2 = A / B if B != 0 else 0
    
    A = get_cnt2(z, w)
    B = cnt_pr[zz]
    s3 = A / B if B != 0 else 0
    
    s4 = cnt_pr[ww] / total_cnt
    
    return s1 * 0.6 + s2 * 0.3 + s3 * 0.099 + s4 * 0.001

# def P2(x, y): # P(y | x)
#     xx = pr2id[x]
#     yy = pr2id[y]
#     lambda_ = 0.98
#     A = get_cnt2(x, y)    
#     return ( A / cnt_pr[xx] * lambda_ if cnt_pr[xx] != 0 else 0 ) + cnt_pr[yy] / total_cnt * (1 - lambda_) # total_cnt!!!

# def P3(x, y, z): # P(z | x, y)
#     xx = pr2id[x]
#     yy = pr2id[y]
#     zz = pr2id[z]
#     lambda_ = 0.98
#     A = get_cnt2(x, y)    
#     return ( A / cnt_pr[xx] * lambda_ if cnt_pr[xx] != 0 else 0 ) + cnt_pr[yy] / total_cnt * (1 - lambda_) # total_cnt!!!


def work(words):
    MAX = float(999999999)
    eps = float(1e-20)
    
    num = len(words)
    f = [{}, {}] # now 3 与 last 3
    ans = [{}, {}]
    
    ANS = ""
    QQQ = MAX
    
    if num == 1:
        for i in yin2pr[words[0]]:
            if cnt_pr[pr2id[i]] != 0:
                tmp = -log(cnt_pr[pr2id[i]] / total_cnt)
                if tmp < QQQ:
                    QQQ = tmp
                    ANS = i[0]
        return ANS
    if num == 2:
        for i1 in yin2pr[words[0]]:
            for i2 in yin2pr[words[1]]:
                tmp = get_cnt2(i1, i2) / cnt_pr[pr2id[i1]] if cnt_pr[pr2id[i1]] != 0 else 0
                tmp = tmp * 0.98 + cnt_pr[pr2id[i2]] / total_cnt * 0.02
                if isclose(tmp, 0, rel_tol=eps):
                    tmp = eps
                tmp = -log(tmp)
                if tmp < QQQ:
                    QQQ = tmp
                    ANS = i1[0] + i2[0]
        return ANS

    for i1 in yin2pr[words[0]]:
        for i2 in yin2pr[words[1]]:
            for i3 in yin2pr[words[2]]:
                a1 = get_cnt3(i1, i2, i3)
                a2 = get_cnt2(i1, i2)
                a3 = get_cnt2(i2, i3)
                c = a1 / a2 if a2 != 0 else 0 
                d = a3 / cnt_pr[pr2id[i2]] if cnt_pr[pr2id[i2]] != 0 else 0
                e = cnt_pr[pr2id[i3]] / total_cnt
                tmp = c * 0.66 + d * 0.33 + e * 0.01
                if isclose(tmp, 0, rel_tol=eps):
                    tmp = eps
                tmp = -log(tmp)
                if tmp < QQQ:
                    QQQ = tmp
                    ANS = i1[0] + i2[0] + i3[0]
                f[0][(i1, i2, i3)] = tmp
                ans[0][(i1, i2, i3)] = i1[0] + i2[0] + i3[0]
    
    for i in range(3, num):
        now = i & 1
        f[now] = {}
        ans[now] = {}
        Q = MAX
        for uu, qq in f[now ^ 1].items():
            i1 = uu[0]
            i2 = uu[1]
            i3 = uu[2]
            for i4 in yin2pr[words[i]]:
                tmp = P(i1, i2, i3, i4)
                if isclose(tmp, 0, rel_tol=eps):
                    tmp = eps
                tmp = qq - log(tmp)
                if tmp > 7 * (i + 1):
                    continue
                if (i2, i3, i4) not in f[now]:
                    f[now][(i2, i3, i4)] = tmp
                    ans[now][(i2, i3, i4)] = ans[now ^ 1][(i1, i2, i3)] + i4[0]
                elif f[now][(i2, i3, i4)] > tmp:
                    f[now][(i2, i3, i4)] = tmp
                    ans[now][(i2, i3, i4)] = ans[now ^ 1][(i1, i2, i3)] + i4[0]
                if f[now][(i2, i3, i4)] < Q:
                    Q = f[now][(i2, i3, i4)]
                    ANS = ans[now][(i2, i3, i4)]
    return ANS, Q / num

for line in tqdm(sys.stdin):
    line_ = line.strip()
    if not line_:
        continue
    words = line_.split()
    print(work(words))