import json

from pathlib import Path
from tqdm import tqdm

pinyin = {}

with open("../拼音汉字表/拼音汉字表/拼音汉字表.txt", encoding="gbk") as f:
    for line in f.readlines():
        parts = line.split()
        for ch in parts[1:]:
            if ch not in pinyin:
                pinyin[ch] = parts[0]

freq = {}
bi_freq = {}


def add(text):
    last = None
    for ch in text:
        if ch not in pinyin:
            last = None
            continue

        freq[ch] = freq.get(ch, 0) + 1
        if last is not None:
            bi_freq[last + ch] = bi_freq.get(last + ch, 0) + 1

        last = ch



for p in Path("../语料库/语料库/sina_news_gbk").rglob("2016-04.txt"):
    for line in tqdm(p.read_text(encoding="gbk").splitlines()):
        obj = json.loads(line)
        add(obj["html"])

uni = {}
for ch in freq:
    if pinyin[ch] not in uni:
        uni[pinyin[ch]] = {"words": [], "counts": []}
    uni[pinyin[ch]]["words"].append(ch)
    uni[pinyin[ch]]["counts"].append(freq[ch])

with open("word2pinyin.txt", "w", encoding="utf-8") as f:
    for a, b in pinyin.items():
        f.write(f"{a} {b}\n")

with open("1_word.txt", "w", encoding="utf-8") as f:
    json.dump(uni, f, ensure_ascii=False, indent=4)

bi = {}
for chs in bi_freq:
    pys = pinyin[chs[0]] + " " + pinyin[chs[1]]
    if pys not in bi:
        bi[pys] = {"words": [], "counts": []}
    bi[pys]["words"].append(chs[0] + ' ' + chs[1])
    bi[pys]["counts"].append(bi_freq[chs])

with open("2_word.txt", "w", encoding="utf-8") as f:
    json.dump(bi, f, ensure_ascii=False, indent=4)
