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
FFF = PREFIX + '/ht_word.txt'

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

with open(FFF, 'r', encoding='utf-8') as f5:
    data5 = json.load(f5)


len_pr = len(id2pr)
cnt_pr = [0] * len_pr

head_pr_cnt = {}
tail_pr_cnt = {}
head_cnt = 0
tail_cnt = 0
for a, b in tqdm(data5.items()):
    head_pr_cnt[(a[0], a[2:])] = b['head_cnt']
    tail_pr_cnt[(a[0], a[2:])] = b['tail_cnt']
    head_cnt += b['head_cnt']
    tail_cnt += b['tail_cnt']

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

def get_cnt3(x, y, z): # cnt(x, y, z)
    strr = x[0] + y[0] + z[0] + x[1] + ' ' + y[1] + ' ' + z[1]
    return DIC.get(strr, 0)

def get_cnt4(x, y, z, s): # cnt(x, y, z, s)
    strr = x[0] + y[0] + z[0] + s[0] +  x[1] + ' ' + y[1] + ' ' + z[1] + ' ' + s[1]
    return DIC.get(strr, 0)

ff = {}

def P2(x, y): # P(y | x)
    if (x, y) in ff:
        return ff[(x, y)]
    a = get_cnt2(x, y) / cnt_pr[pr2id[x]] if cnt_pr[pr2id[x]] != 0 else 0
    ff[(x, y)] = 0.98 * a + 0.02 * cnt_pr[pr2id[y]] / total_cnt
    return ff[(x, y)]

def P3(x, y, z): # P(z | x,y)
    if (x, y, z) in ff:
        return ff[(x, y, z)]
    we = get_cnt2(x, y)
    a = get_cnt3(x, y, z) / we if we != 0 else 0
    ff[(x, y, z)] = 0.98 * a + 0.02 * P2(y, z)
    return ff[(x, y, z)]

def P4(x, y, z, w): # P(w | x,y,z)
    if (x, y, z, w) in ff:
        return ff[(x, y, z, w)]
    
#    zz = pr2id[z]
#    ww = pr2id[w]
    A = get_cnt4(x, y, z, w)
    B = get_cnt3(x, y, z)
    s1 = A / B if B != 0 else 0

    ff[(x, y, z, w)] = 0.98 * s1 + 0.02 * P3(y, z, w)
    return ff[(x, y, z, w)]

def P(y, z, w): # P(w | x,y,z)
    zz = pr2id[z]
    ww = pr2id[w]    
    A = get_cnt3(y, z, w)
    B = get_cnt2(y, z)
    s2 = A / B if B != 0 else 0
    
    A = get_cnt2(z, w)
    B = cnt_pr[zz]
    s3 = A / B if B != 0 else 0
    
    s4 = cnt_pr[ww] / total_cnt
    
    return s2 * 0.6 + s3 * 0.398 + s4 * 0.002


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
 #               tmp = tmp * 0.98 + cnt_pr[pr2id[i2]] / total_cnt * 0.02
                tmp *= 0.5 * head_pr_cnt.get(i1, 0) / head_cnt + 0.5 * cnt_pr[pr2id[i1]] / total_cnt
                if isclose(tmp, 0, rel_tol=eps):
                    tmp = eps
                tmp = -log(tmp)
                if tmp < QQQ:
                    QQQ = tmp
                    ANS = i1[0] + i2[0]
        return ANS

    for i1 in yin2pr[words[0]]:
        for i2 in yin2pr[words[1]]:
            # P(i1 | h)
            e = 0.1 * head_pr_cnt.get(i1, 0) / head_cnt + 0.9 * cnt_pr[pr2id[i1]] / total_cnt
            
            # P(i2 | i1 h) = P(i2 | i1)
            o = P2(i1, i2)

            if isclose(e, 0, rel_tol=eps):
                e = -log(eps)
            else :
                e = -log(e)
            
            if isclose(o, 0, rel_tol=eps):
                o = -log(eps)
            else :
                o = -log(o)
            
            tmp = e + o
            if tmp < QQQ:
                QQQ = tmp
                ANS = i1[0] + i2[0]
            f[0][(i1, i2)] = tmp
            ans[0][(i1, i2)] = i1[0] + i2[0]
    
    for i in range(2, num):
        now = (i % 2) ^ 1
        f[now] = {}
        ans[now] = {}
        Q = MAX
        for i1 in yin2pr[words[i - 2]]:
            for i2 in yin2pr[words[i - 1]]:
                if (i1, i2) not in f[now ^ 1]:
                    continue
                for i3 in yin2pr[words[i]]:
                    tmp = P(i1, i2, i3)
                    if isclose(tmp, 0, rel_tol=eps):
                        tmp = eps
                    tmp = f[now ^ 1][(i1, i2)] - log(tmp)
#                    if tmp > 7 * num:
#                        continue
                    if (i2, i3) not in f[now]:
                        f[now][(i2, i3)] = tmp
                        ans[now][(i2, i3)] = ans[now ^ 1][(i1, i2)] + i3[0]
                    elif f[now][(i2, i3)] > tmp:
                        f[now][(i2, i3)] = tmp
                        ans[now][(i2, i3)] = ans[now ^ 1][(i1, i2)] + i3[0]
                    if f[now][(i2, i3)] < Q:
                        Q = f[now][(i2, i3)]
                        ANS = ans[now][(i2, i3)]
    return ANS #, Q / num

for line in tqdm(sys.stdin):
    line_ = line.strip()
    if not line_:
        continue
    words = line_.split()
    print(work(words))
