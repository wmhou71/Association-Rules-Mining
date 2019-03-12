import re
import copy
import itertools


class Item:

    '''物品項目'''
    keys = []
    support = 0.0

    def __init__(self, keys, support=0.0):
        self.keys = keys
        self.support = support

    def getSubset(self, size, k):  # -----求出子集合
        subset = []
        if k == 1:
            for i in range(size):
                subset.append([self.keys[i]])
            return subset
        else:
            i = size - 1
            while i >= k-1:
                orig_set = self.getSubset(i, k-1)
                j = 0
                while j < len(orig_set):
                    orig_set[j] += [self.keys[i]]
                    j += 1
                subset += (orig_set)
                i -= 1
            return subset

    def checkDiff(self, items):  # ------檢查串列值是否符合條件
        length = len(self.keys)
        if length != len(items.keys) or self.keys == items:
            return False
        return self.keys[0:-1] == items.keys[0:-1]

    def add(self, items):  # ------增加鍵(key)
        temp = copy.copy(self.keys)
        temp.insert(
            len(self.keys), items.keys[len(items.keys) - 1])
        it = Item(temp, 0.0)
        return it

    def __str__(self):
        return_string = '{ '
        for key in self.keys:
            return_string += key+','
        return_string += ' }'+' (support:%.3f)\n' % (self.support)
        return return_string


class Candidate:

    '''候選項目集集合'''

    keys = []
    k = 0

    def __init__(self, keys, k):
        self.keys = keys
        self.k = k

    def getL(self, threshold):  # -----求高頻項目集集合
        items = []
        for item in self.keys:
            if item.support >= threshold:
                items.append(copy.copy(item))
        if len(items) == 0:
            return Large([], self.k)
        return Large(copy.deepcopy(items), self.k)

    def __str__(self):
        return_string = str(self.k)+'-itemset:' + \
            str(len(self.keys))+' \r\n '
        for key in self.keys:
            if True == isinstance(key, Item):
                return_string += key.__str__()
        return return_string


class Large:

    '''高頻項目集集合'''

    items = []
    k = 0

    def __init__(self, items, k):
        self.items = items
        self.k = k

    def checkFrequentItemsets(self, item):  # -----檢查高頻項目集合是否過條件
        subs = item.getSubset(len(item.keys), self.k)
        for each in subs:
            tag = False
            for i in self.items:
                if i.keys == each:
                    tag = True
                    break
            if tag == False:
                return True
        return False

    def aprioriGen(self):  # -----Apriori Property 高頻集合其子集合也為高頻
        outcome = []
        for i in range(len(self.items)):
            for j in range(i+1, len(self.items)):
                if self.items[i].checkDiff(self.items[j]):
                    item = self.items[i].add(self.items[j])
                    if False == self.checkFrequentItemsets(item):
                        outcome.append(item)
        if(len(outcome) == 0):
            return Candidate([], self.k+1)
        return Candidate(outcome, self.k+1)

    def __str__(self):
        return_string = "\r\n" + \
            str(self.k) + '-itemsets : '+str(len(self.items))+"\r\n"
        for item in self.items:
            return_string += item.__str__()
        return return_string


class SaveReport:

    '''紀錄1-itemset到k-itemset'''

    values = {}

    def get(self, k):
        return self.values[k]

    def put(self, l, k):
        self.values[k] = l

    def __str__(self):
        return_string = '========Outcome report========\r\n'
        for l in self.values:
            return_string += self.values[l].__str__()
        return return_string


class Rule:
    confidence = .0
    lift = .0
    strong_rule = ''

    def __init__(self, confidence, lift, strong_rule):
        self.confidence = confidence
        self.lift = lift
        self.strong_rule = strong_rule

    def __str__(self):
        return 'Rule:' + self.strong_rule + '  confidence: %.3f' % (self.confidence) + '  lift: %.3f' % (self.lift)


class Apriori:

    def __init__(self, min_support=0.10, datafile='apriori.data'):  # -----讀檔
        inputfile = open(datafile, "r")
        self.data = []
        self.min_support = min_support
        for line in inputfile.readlines()[1:]:
            tmp = []
            for key in line[0:-2].split(" "):
                tmp.append(key)
            self.data.append(tmp)

    def bulidFirstFrequentItemsets(self):  # -----建立L1
        count = {}
        items = []
        for temp in self.data:
            for key in temp:
                if key in count:
                    count[key] += 1
                else:
                    count[key] = 1

        for key in count:
            if count[key]/len(self.data) >= self.min_support:
                items.append(Item([key], count[key]/len(self.data)))

        temp = Large(copy.deepcopy(items), 1)
        return temp

    # -----求出confidence和lift
    def ralationRules(self, maxSequence, min_confidence):
        rules = []
        for each in maxSequence:
            for i in range(len(each.keys)-1):
                subsets = each.getSubset(len(each.keys), i+1)
                for subset in subsets:
                    count = 0
                    for tran_item in self.data:
                        tag = False
                        for key in subset:
                            if key not in tran_item:
                                tag = True
                                break
                        if tag == False:
                            count += 1
                    confidence = (each.support*len(self.data))/count
                    lift = confidence / (count/len(self.data))
                    if confidence >= min_confidence:
                        str_rule = str(set(subset)) + '-->' + \
                            str(set(each.keys)-set(subset))
                        rule = Rule(confidence, lift, str_rule)
                        rules.append(rule)
        return rules

    def run(self):
        sr = SaveReport()
        oneitemset = self.bulidFirstFrequentItemsets()
        sr.put(oneitemset, 1)
        k = 2

        while len(sr.values) != 0:  # -----紀錄出現次數
            candidate = sr.get(k - 1).aprioriGen()
            if len(candidate.keys) == 0:
                break
            for each in candidate.keys:
                count = 0
                for each_src in self.data:
                    if len(each_src) < len(each.keys):
                        pass
                    else:
                        tag = True
                        for just_one_e in each.keys:
                            tag = just_one_e in each_src
                            if tag == False:
                                break
                        if tag == True:
                            count += 1

                each.support = count/len(self.data)
            sr.put(candidate.getL(a.min_support), k)
            k += 1
        return sr

min_support = input('Please key in minimum support [0 ~ 1]：')
min_confidence = input('Please key in minimum confidence [0 ~ 1]：')

a = Apriori(float(min_support), 'input.txt')
sr = a.run()
print(sr)

print("\n-----------Strong Rules-----------")
print(sr.get(len(sr.values)))
rules = a.ralationRules(sr.get(len(sr.values)).items, float(min_confidence))
for rule in rules:
    print(rule)

