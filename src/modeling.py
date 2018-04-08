import sys
import re
import time
import os

'''
Author: Yinghui Jiang

Date: 2018/01/19
'''


class modeling:
    # init function
    def __init__(self, trainFile, testFile):
        self.trainFile = os.path.join('../data', trainFile)
        self.testFile = os.path.join('../data', testFile)
        self.unigramDic = {}  # save the word-count map of unigram
        self.bigramDic = {}  # save the word-count map of bigram
        self.UniLength = 0  # the length of unigram model
        self.BiLength = 0  # the length of bigram model
        self.TYPE = ["UNIGRAM", "BIGRAM", "SMOOTH"]  # the model type list
        self.ANSWERS = ["whether", "through", "piece", "court", "allowed", "check", "hear", "cereal", "chews",
                        "sell"]  # the  correct answer list

    # get the words of the content
    def segment(self, text):
        p = re.compile(r"([A-Za-z0-9]+)")  # move the punctuation, keep the words and numbers
        return list(p.findall(text))  # return the list of words

    # training the unigram model
    def trainUnigramModel(self, texts):
        for content in texts:
            words = self.segment(content.lower())
            self.unigram(words)
        self.UniLength = len(self.unigramDic)

    # traning the bigram model
    def trainBigramModel(self, texts):
        for content in texts:
            words = self.segment(content.lower())
            words.insert(0, "none")
            words.insert(len(words), "none")
            self.bigram(words)
        self.BiLength = len(self.bigramDic)

    #  the model of unigram
    def unigram(self, words):
        for word in words:
            if (word not in self.unigramDic):
                self.unigramDic[word] = 1
            else:
                self.unigramDic[word] += 1

    # the model of bigram
    def bigram(self, words):
        flag = 0
        biStr = ""
        for word in words:
            flag += 1
            if (flag == 2):  # flag equal 2 means the bi-words consisted succeed
                biStr = biStr + " "
            biStr = biStr + word
            if (flag == 2):
                if (biStr not in self.bigramDic):
                    self.bigramDic[biStr] = 1
                else:
                    self.bigramDic[biStr] += 1
                flag = 1
                biStr = word

    # get the content of the text file
    def readFile(self, fileName):
        with open(fileName, 'r+') as file:
            text = file.read()
        return text

    def readFileByLine(self, fileName):
        file = open(fileName, 'r')
        lineList = []
        for line in file:
            lineList.append(line)
        return lineList

    # get the question sentence and the optional answer
    def getQuestions(self, content):
        patternA = re.compile(r".*? : (\w+)/(\w+)")  # to match the optional answer
        patternQ = re.compile(r"(.*?) . : .*?")  # to match the question sentence
        return patternQ.findall(content), patternA.findall(content)

    # get the best answer
    def rankAnswer(self, questions, answers, type):
        QA_Set = ["" for x in range(len(answers))]
        for i in range(len(answers)):
            QA_Set[i] = questions.replace("____", answers[i])  # replace the "____"(blank) to the option answer
        if (type == self.TYPE[0]):
            self.rankAnswerByUnigram(QA_Set, answers, 1)  # smoothing is 1
        elif (type == self.TYPE[1]):
            self.rankAnswerByBigram(QA_Set, answers)  # smoothing is 0
        elif (type == self.TYPE[2]):
            self.rankAnswerByBigram(QA_Set, answers, 1)  # smoothing is 1

    # acaculate the probobility of the sentence by Unigram with smoothing or not
    def rankAnswerByUnigram(self, contents, answers, smoothing=0):
        sum = 0.0
        index = 0
        for i in range(len(contents)):  # i is the index of the sum
            words = self.segment(contents[i])
            words.insert(0, "none")
            words.insert(len(words), "none")
            temp = 1
            for word in words:
                if (word not in self.unigramDic.keys()):
                    temp *= self.unigramDic.get(word, smoothing) / (self.UniLength + smoothing * self.UniLength)
                else:
                    temp *= self.unigramDic[word] / self.UniLength
            if (temp >= sum and temp != 1):  # record the index of the largest probability
                index = i
                sum = temp
        print(answers[index], self.checkAnswer(answers[index]), sum)

    # acaculate the probobility of the sentence by Bigram with smoothing or not
    def rankAnswerByBigram(self, contents, answers, smoothing=0):
        sum = 0.0
        index = 0
        for i in range(len(contents)):
            words = self.segment(contents[i])
            words.insert(0, "none")
            words.insert(len(words), "none")
            flag = 0
            biStr = ""
            temp = 1
            for word in words:
                flag += 1
                if (flag == 2):  # flag equal 2 means the bi-words consisted succeed
                    biStr = biStr + " "
                biStr = biStr + word
                if (flag == 2):
                    if (biStr not in self.bigramDic.keys()):
                        pro = self.bigramDic.get(biStr, smoothing) / (self.BiLength + smoothing * self.BiLength)
                        ########
                        # self.showBigram(biStr, pro)
                        ########
                        temp *= pro
                    else:
                        pro = self.bigramDic[biStr] / self.BiLength
                        ########
                        # self.showBigram(biStr, pro)
                        ########
                        temp *= pro
                    flag = 1
                    biStr = word
            if (temp >= sum and temp != 1):  # record the index of the largest probability
                index = i
                sum = temp
        if (sum != 0):
            print(answers[index], self.checkAnswer(answers[index]), sum)
        else:
            print("No answer! The both probability of this question is 0")

    # check the answer is correct or not
    def checkAnswer(self, answer):
        return answer in self.ANSWERS

    def showBigram(self, strBi, prob):
        print(strBi, ":", prob)


# this is the main function
# news-corpus-500k.txt questions.txt
if __name__ == '__main__':
    trainFile, testFile = "", ""
    if len(sys.argv) != 3:
        print("Error Command!")
        exit(0)
    else:
        trainFile = sys.argv[1]  # get the training file name
        testFile = sys.argv[2]  # get the testing file name
    startTime = time.time()  # start time
    NgramTest = modeling(trainFile, testFile)
    texts = NgramTest.readFileByLine(NgramTest.trainFile)  # get the train text
    questions = NgramTest.readFile(NgramTest.testFile)  # get the test text
    questionSet, answerSet = NgramTest.getQuestions(questions.lower())  # get the questionSet and optional answerSet
    NgramTest.trainUnigramModel(texts)  # training the unigram model
    NgramTest.trainBigramModel(texts)  # training the bigram model
    for type in NgramTest.TYPE:  # show the result
        print(type)
        for index in range(len(questionSet)):
            NgramTest.rankAnswer(questionSet[index], answerSet[index], type)
    endTime = time.time()  # end time
    print(endTime - startTime, "s")  # show the time cost
