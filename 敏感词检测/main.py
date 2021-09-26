#import sys
from langconv import *
import copy
import pypinyin
from Radical import getRadical, is_leftandright

pinandzi = []
MaxMatchType=2

file_words = sys.argv[1]
file_org = sys.argv[2]
file_ans = sys.argv[3]

class Word:  # 构建敏感词库
    def __init__(self, word):
        self.original_word = word

    def confuse(self):
        """
        构造敏感词的汉字、拼音、首字母、偏旁部首的混合
        :param:
        return:混合后敏感词库
        """
        sen_thesaurus = []
        word = list(self.original_word)

        for i in range(len(word)):
            c = word[i]
            # 汉字
            if (u'\u4e00' <= c <= u'\u9fa5') or (u'\u3400' <= c <= u'\u4db5'):  # 常见字、繁体字、不常见字
                li = []
                # pinyin
                pin = pypinyin.lazy_pinyin(c)
                gap = ''
                # print(self.pinandzi)
                li.append(c)
                pin = pin[0]
                li.append(pin[0])  # 首字母
                temp_pin=[]
                for keypin in pin:
                    temp_pin.append(keypin)
                li.append(temp_pin)  # 全拼
                hanzi_part=[]
                if is_leftandright(c):
                    hanzi_part = getRadical(c)
                    li.append(hanzi_part)

                word[i] = li  # 一个词添加完毕
                pinandzi.append([c , gap.join(pin), pin[0]]+ hanzi_part)

            else:
                pass
        for c in word:
            # 开始混合
            # 英文跳过
            if not isinstance(c, list):
                if len(sen_thesaurus) == 0:
                    sen_thesaurus.append([c])
                else:
                    for li in sen_thesaurus:
                        li.append(c)
            # 中文拼音偏旁部首混合
            else:
                if len(sen_thesaurus) == 0:
                    for alist in c:
                        if not isinstance(alist, list):
                            sen_thesaurus.append([alist])
                        else:
                            sen_thesaurus.append(alist)
                else:
                    temp = sen_thesaurus
                    new_confuse_enum = []
                    for alist in c:
                        new_confuse = copy.deepcopy(temp)
                        if not isinstance(alist, list):
                            for cur_confuse in new_confuse:
                                cur_confuse.append(alist)
                        else:
                            for cur_confuse in new_confuse:
                                for x in alist:
                                    cur_confuse.append(x)
                        new_confuse_enum = new_confuse_enum + new_confuse
                    sen_thesaurus = new_confuse_enum
        return sen_thesaurus

class DFAUtils(object):
    """
    DFA算法
    """

    def __init__(self):
        """
        算法初始化
        :param :
        """
        # 词库
        self.root = dict()
        # 无意义词库,在检测中需要跳过的（这种无意义的词最后有个专门的地方维护，保存到数据库或者其他存储介质中）
        self.skip_root = [' ', '&', '!', '！', '@', '#', '$', '￥', '*', '^', '%', '?', '？', '<', '>', "《", '》']
        self.confused_words=[]
        self.__line_cnt = 0
        self.pinandzi = []
        self.total = 0
        self.result = []
        self.originsen=[]
        self.sennub=0

    def addword(self, word):
        """
        添加词库
        :param word:敏感词
        :return:
        """
        now_node = self.root
        word_count = len(word)
        for i in range(word_count):
            char_str = word[i]
            if char_str in now_node.keys() :
                # 如果存在该key，直接赋值，用于下一个循环获取
                now_node = now_node.get(word[i])
                #if word[i] =='f':
                    #print(now_node)
                now_node['is_end'] = False
                if  i==word_count-1:
                    now_node['short'] = True
                if now_node['short']:
                    now_node['is_end']=True
                now_node['orgin'] = self.originsen[self.sennub]
            else:
                # 不存在则构建一个dict
                new_node = dict()

                if i == word_count - 1:  # 最后一个
                    new_node['is_end'] = True
                    new_node['word']=word
                    new_node['short']=True
                else:  # 不是最后一个
                    new_node['is_end'] = False
                    new_node['short'] = False

                now_node[char_str] = new_node
                now_node = new_node
                now_node['orgin'] = self.originsen[self.sennub]
        # 加载敏感词库函数

    def parse(self, path):
        """
        读取敏感词文件
        :param path:敏感词文件路径
        :return:
        """
        confused_word_list = []
        with open(path, encoding='utf-8') as f:
            for keyword in f:  # 跳去构建扩大敏感词树
                self.originsen.append(str(keyword).strip())
                confuse = Word(str(keyword).strip())
                confused_word_list.append(confuse.confuse())
        gap = ''
        for words in confused_word_list:
            for keyword in words:
                self.addword(gap.join(keyword))
            self.sennub +=1
        self.confused_words = confused_word_list

    def subtongyin(self, acha, content):
        """
        谐音字处理
        :param acha:检测字符的前一个字符
        :param content:待检测字符
        :return:谐音字对应敏感字中文字符样式
        """
        for i in range(len(content)):
            flag = False
            cur_word = content[i]
            curpy = pypinyin.lazy_pinyin(cur_word)
            gap = ''
            curpy = gap.join(curpy)
            for words in pinandzi:  # 获取敏感词对象
                if curpy == words[1] and (cur_word not in words or acha not in words):
                    flag = True  # 判断 该字的拼音 是否在 某个敏感词对象的拼音列表里
                    temp = content[:i] + words[0] + content[i + 1:]  # 如果在进行替换同音字，把同音字换成敏感词中的字
                    content = temp
                    break  # 找到了就不去下一个敏感词里查找了
                if flag:
                    break
        return content

    def check_match_word(self, txt, begin_index, match_type=MaxMatchType):
        """
        检查文字中是否包含匹配的字符
        :param txt:待检测的文本
        :param begin_index: 调用getSensitiveWord时输入的参数，获取词语的上边界index
        :param match_type:匹配规则最大匹配规则
        :return:如果存在，则返回匹配字符的长度，不存在返回0
        """
        flag = False
        match_flag_length = 0  # 匹配字符的长度
        now_map = self.root
        tmp_flag = 0  # 包括特殊字符的敏感词的长度
        word1=''

        for i in range(begin_index, len(txt)):
            word = txt[i]

            # 检测是否是特殊字符"
            if (u'\u4e00' <= word <= u'\u9fa5'):
                word = self.subtongyin(txt[i - 1], word)
            elif ('a' <= word <= 'z'):
                word = word
            elif (u'\u3400' <= word <= u'\u4db5'):
                word = Converter('zh-hans').convert(word)
            elif ('A' <= word <= 'Z'):
                word = word.lower()
            else:
                if flag:
                    break
                tmp_flag += 1
                continue
            # 获取指定key

            now_map = now_map.get(word)
            if now_map:  # 存在，则判断是否为最后一个
                # 找到相应key，匹配标识+1
                match_flag_length += 1
                tmp_flag += 1
                # 如果为最后一个匹配规则，结束循环，返回匹配标识数
                if now_map.get("is_end"):
                    # 结束标志位为true
                    word1=now_map.get('orgin')
                    flag = True
            else:  # 不存在，直接返回
                break

        if tmp_flag < 2 or not flag:  # 长度必须大于等于1，为词
            tmp_flag = 0
        return tmp_flag,word1

    def get_match_word(self, txt, match_type=MaxMatchType):
        """
        获取匹配到的词语
        :param txt:待检测的文本
        :param match_type:匹配规则 最大匹配规则
        :return:文字中的相匹配词
        """
        result=[]
        s=[]
        word1 = ''
        matched_word_list = list()
        for i in range(len(txt)):  # 0---11
            words=txt[i]
            if (u'\u4e00' <= words <= u'\u9fa5') or ('a' <= words <= 'z') or ('A' <= words <= 'Z') or (u'\u3400' <= words <= u'\u4db5'):
                pass
            else:
                continue

            length,word1 = self.check_match_word(txt, i, match_type)
            if length > 0:
                word = txt[i:i + length]
                matched_word_list.append(word)
                i = i + length-1
                self.total+=1
                gap=''
                result.append(word1)
                result.append(self.__line_cnt)
                result.append(gap.join(matched_word_list))
                self.result.append(result)
                result=[]
                matched_word_list=[]
        return matched_word_list

    def read_org(self, path):
        """
        读取待敏感词检测文本文件
        :param path:读取文件路径
        :return:
        """
        try:  # 异常处理
            with open(path, 'r+', encoding='utf-8') as org:
                lines = org.readlines()
                for line in lines:
                    line = line.strip()
                    self.__line_cnt += 1
                    self.get_match_word(line)
        except IOError:
            raise IOError("[filter] Unable to open the file to be detected")
        #lines='FaLGFaLGFaLG'


    def out_ans(self, path):
        """
        将结果输出到文本
        :param path:输出文件路径
        :return:
        """
        try:
            with open(path, 'w+', encoding='utf-8') as ans:
                print("Total: {}".format(self.total), file=ans)
                for i in self.result:
                    print('Line{}: <{}> {}'.format(i[1], i[0], i[2]), file=ans)
        except IOError:
            raise IOError("[answer export] Unable to open ans file")


if __name__ == '__main__':
    dfa = DFAUtils()
    #path = 'C:/keep/words.txt'
    dfa.parse(file_words)
    #pathorg = 'C:/keep/org.txt'
    dfa.read_org(file_org)
    #pathans = 'C:/keep/ans.txt'
    dfa.out_ans(file_ans)


