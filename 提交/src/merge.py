import json
from tqdm import tqdm
Dic = {}
# Lis = ["./1_word4 1 to 20000.txt", 
#        "./1_word4 20001 to 40000.txt",
#        "./1_word4 40001 to 60000.txt",
#        "./1_word4 60001 to 600000.txt",
#        ]
Lis = ["./4_word0.txt", 
       "./4_word1.txt",
       "./4_word4.txt",
       "./4_word5.txt",
       "./4_word6.txt",
       "./4_word7.txt",
       "./4_word8.txt",
       "./4_word9.txt",
       ]
target = "./4_word.txt"


for _ in Lis:
    with open(_, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # for a, b in tqdm(data.items()):
        #     if a in Dic:
        #         Dic[a]['head_cnt'] += b['head_cnt']
        #         Dic[a]['tail_cnt'] += b['tail_cnt']
        #     else :
        #         Dic[a] = b
        for a, b in tqdm(data.items()):
            if a in Dic:
                for __ in range(len(b['words'])):
                    try :
                        id = Dic[a]['words'].index(b['words'][__])
                        Dic[a]['counts'][id] += b['counts'][__]
                    except:
                        Dic[a]['words'].append(b['words'][__])
                        Dic[a]['counts'].append(b['counts'][__])
            else :
                Dic[a] = b

with open(target, 'w', encoding='utf-8') as f:
    json.dump(Dic, f, ensure_ascii=False, indent=4)