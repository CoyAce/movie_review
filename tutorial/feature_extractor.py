# coding=utf-8

from itertools import chain
from pickle import dump
from nltk import bigrams
from nltk.classify.scikitlearn import SklearnClassifier
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from nltk.probability import FreqDist, ConditionalFreqDist
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.svm import SVC, LinearSVC, NuSVC


# Feature extraction function
def bag_of_words(words):
    """
    Use all words as features
    """
    return dict([(word, True) for word in words])


def bigram(words, score_function=BigramAssocMeasures.chi_sq, top_n=200):
    """
    Use bigrams as features (use chi square chose top 200 bigrams)
    """
    bigram_finder = BigramCollocationFinder.from_words(words)
    bigrams = bigram_finder.nbest(score_function, top_n)
    return bag_of_words(bigrams)


def bigram_words(words, score_function=BigramAssocMeasures.chi_sq, n=200):
    """
    Use words and bigrams as features (use chi square chose top 200 bigrams)
    """
    bigram_finder = BigramCollocationFinder.from_words(words)
    bigrams = bigram_finder.nbest(score_function, n)
    return bag_of_words(words + bigrams)


# 计算每个词的信息熵，提取信息量最大的词作为特征词
def calculate_word_scores(positive_data, negative_data):
    positive_words, negative_words = chain_words(positive_data, negative_data)
    return calculate_score(positive_words, negative_words)


def calculate_bigram_scores(positive_data, negative_data):
    positive_words, negative_words = chain_words(positive_data, negative_data)

    positive_bigram_finder = BigramCollocationFinder.from_words(positive_words)
    negative_bigram_finder = BigramCollocationFinder.from_words(negative_words)
    positive_bigrams = positive_bigram_finder.nbest(BigramAssocMeasures.chi_sq, 8000)
    negative_bigrams = negative_bigram_finder.nbest(BigramAssocMeasures.chi_sq, 8000)

    return calculate_score(negative_bigrams, positive_bigrams)


def calculate_word_bigram_scores(positive_data, negative_data):
    """
    Combine words and bigrams information scores
    """
    positive_words, negative_words = chain_words(positive_data, negative_data)

    positive_bigram_finder = BigramCollocationFinder.from_words(positive_words)
    negative_bigram_finder = BigramCollocationFinder.from_words(negative_words)
    positive_bigrams = positive_bigram_finder.nbest(BigramAssocMeasures.chi_sq, 5000)
    negative_bigrams = negative_bigram_finder.nbest(BigramAssocMeasures.chi_sq, 5000)

    return calculate_score(negative_words + negative_bigrams, positive_words + positive_bigrams)


def chain_words(positive_data, negative_data):
    positive_words = list(chain(*positive_data))
    negative_words = list(chain(*negative_data))
    return positive_words, negative_words


def calculate_score(positive_words, negative_words):
    # 频率分布
    conditional_word_frequency_distribution, word_frequency_distribution = calculate_frequency(positive_words,
                                                                                               negative_words)
    positive_word_count = conditional_word_frequency_distribution['pos'].N()
    negative_word_count = conditional_word_frequency_distribution['neg'].N()
    total_word_count = positive_word_count + negative_word_count
    word_scores = {}
    for word, freq in word_frequency_distribution.iteritems():
        positive_score = BigramAssocMeasures.chi_sq(conditional_word_frequency_distribution['pos'][word],
                                                    (freq, positive_word_count), total_word_count)
        negative_score = BigramAssocMeasures.chi_sq(conditional_word_frequency_distribution['neg'][word],
                                                    (freq, negative_word_count), total_word_count)
        word_scores[word] = positive_score + negative_score
    return word_scores


def calculate_frequency(positive_words, negative_words):
    word_frequency_distribution = FreqDist()
    conditional_word_frequency_distribution = ConditionalFreqDist()
    for word in positive_words:
        word_frequency_distribution[word] += 1
        conditional_word_frequency_distribution['pos'][word] += 1
    for word in negative_words:
        word_frequency_distribution[word] += 1
        conditional_word_frequency_distribution['neg'][word] += 1
    return conditional_word_frequency_distribution, word_frequency_distribution


# 5 Second we should extact the most informative words or bigrams based on the information score
def find_best_words(word_scores, number):
    best_vals = sorted(word_scores.iteritems(), key=lambda (w, s): s, reverse=True)[:number]
    best_words = set([w for w, s in best_vals])
    return best_words


# 6 Third we could use the most informative words and bigrams as machine learning features
# Use chi_sq to find most informative words of the review
def best_word_features(words, best_words):
    return dict([(word, True) for word in words if word in best_words])


# Use chi_sq to find most informative bigrams of the review
def best_bigram_features(words, best_words):
    return dict([(word, True) for word in bigrams(words) if word in best_words])


# Use chi_sq to find most informative words and bigrams of the review
def best_combined_features(words, best_words):
    best_word_feature = best_word_features(words, best_words)
    best_bigram_feature = best_bigram_features(words, best_words)
    combined_feature = dict(best_word_feature, **best_bigram_feature)
    return combined_feature


# 7 Transform review to features by setting labels to words in review
def set_positive_label(positive_reviews, feature_extraction_method, best_words):
    posFeatures = []
    for i in positive_reviews:
        posWords = [feature_extraction_method(i, best_words), 'pos']
        posFeatures.append(posWords)
    return posFeatures


def set_negative_label(negative_reviews, feature_extraction_method, best_words):
    negFeatures = []
    for i in negative_reviews:
        negWords = [feature_extraction_method(i, best_words), 'neg']
        negFeatures.append(negWords)
    return negFeatures


def clf_score(classifier, train_set, test, tag_test):
    classifier = SklearnClassifier(classifier)
    classifier.train(train_set)
    predict = classifier.classify_many(test)
    return accuracy_score(tag_test, predict)


def cal_classifier_accuracy(train_set, test, tag_test):
    classifierlist = []
    print '各个分类器准度：'
    print 'BernoulliNB`s accuracy is %f' % clf_score(BernoulliNB(), train_set, test, tag_test)
    print 'MultinomiaNB`s accuracy is %f' % clf_score(MultinomialNB(), train_set, test, tag_test)
    print 'LogisticRegression`s accuracy is %f' % clf_score(LogisticRegression(), train_set, test, tag_test)
    print 'SVC`s accuracy is %f' % clf_score(SVC(gamma=0.001, C=100., kernel='linear'), train_set, test, tag_test)
    print 'LinearSVC`s accuracy is %f' % clf_score(LinearSVC(), train_set, test, tag_test)
    print 'NuSVC`s accuracy is %f' % clf_score(NuSVC(), train_set, test, tag_test)
    # print 'GaussianNB`s accuracy is %f' %clf_score(GaussianNB())
    classifierlist.append([BernoulliNB(), clf_score(BernoulliNB(), train_set, test, tag_test)])
    classifierlist.append([MultinomialNB(), clf_score(MultinomialNB(), train_set, test, tag_test)])
    classifierlist.append([LogisticRegression(), clf_score(LogisticRegression(), train_set, test, tag_test)])
    classifierlist.append([SVC(gamma=0.001, C=100., kernel='linear'),
                           clf_score(SVC(gamma=0.001, C=100., kernel='linear'), train_set, test, tag_test)])
    classifierlist.append([LinearSVC(), clf_score(LinearSVC(), train_set, test, tag_test)])
    classifierlist.append([NuSVC(), clf_score(NuSVC(), train_set, test, tag_test)])
    return classifierlist


def find_best_classifier(classifiers):
    max_val = 0
    for c in classifiers:
        if c[1] > max_val:
            max_val = c[1]
            best = c[0]
    return best


def store_classifier(object, train_set, path):
    object_classifier = SklearnClassifier(object)
    object_classifier.train(train_set)
    dump(object_classifier, open(path + '/classifier.pkl', 'w'))


# 4. 加载分类器
# clf = pickle.load(open(path+'/classifier.pkl'))

# 计算测试集的概率
# pred = clf.prob_classify_many(extract_features(test_review))

# 保存
def store_predict_result(path, pred):
    p_file = open(path + '/result/result.txt', 'w')
    for i in pred:
        p_file.write(str(i.prob('pos')) + ' ' + str(i.prob('neg')) + '\n')
    p_file.close()

    pred2 = []
    pos_count = 0
    neg_count = 0
    for i in pred:
        pred2.append([i.prob('pos'), i.prob('neg')])
        if i.prob('pos') > i.prob('neg'):
            pos_count += 1
        else:
            neg_count += 1

    print '好评占：', '%f' % ((pos_count * 1.0) / ((pos_count + neg_count) * 1.0))
    print '差评占：', '%f' % ((neg_count * 1.0) / ((pos_count + neg_count) * 1.0))


def extract_features(dataset, best_words):
    feat = []
    for i in dataset:
        #         feat.append(best_word_features(i,best_words))
        feat.append(best_combined_features(i, best_words))
    return feat
