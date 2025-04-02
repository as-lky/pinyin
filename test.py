with open('./answer.txt', 'r', encoding='utf-8') as f:
    answer_lines = f.readlines()
    
with open('./output.txt', 'r', encoding='gbk') as f:
    output_lines = f.readlines()

answer_lines = answer_lines[:len(output_lines)]    
assert len(answer_lines) == len(output_lines)

sentence_ok = 0
sentence_cnt = 0
word_ok = 0
word_cnt = 0
for i in range(len(answer_lines)):
    if answer_lines[i].strip() == None:
        break
    sentence_cnt = sentence_cnt + 1
    answer_line = answer_lines[i].strip()
    output_line = output_lines[i].strip()
    if answer_line == output_line:
        sentence_ok = sentence_ok + 1
    
    word_cnt += len(answer_line)
    word_ok += sum([1 for a, b in zip(answer_line, output_line) if a == b])
    
print('sentence ok: %d, cnt: %d, acc: %.5f' % (sentence_ok, sentence_cnt, sentence_ok / sentence_cnt))
print('word ok: %d, cnt: %d, acc: %.5f' % (word_ok, word_cnt, word_ok / word_cnt))
    