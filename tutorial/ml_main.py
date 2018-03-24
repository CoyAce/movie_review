# coding=utf-8
import feature_extractor
import text_processing  # 处理excel或者txt类
import pickle
from random import shuffle
from nltk.classify.scikitlearn import SklearnClassifier
import os
import time

if __name__ == "__main__":
    print '开始训练分类器'
    # 1. Load positive and negative review data
    path = os.getcwd()
    print '当前路径' + path
    start_time = time.time()

    positive_reviews = text_processing.load_data_and_segment_sentences(path + "/seniment review set/THREEMIXPOS.xls")
    negative_reviews = text_processing.load_data_and_segment_sentences(path + "/seniment review set/THREEMIXNEG.xls")
    test_review = text_processing.load_data_and_segment_sentences(path + "/seniment review set/THREEMIXTEST.xls")

    # 2. Feature extraction function
    # Choose word_scores extaction methods
    # word_scores = create_word_scores()
    # word_scores = create_bigram_scores()
    word_scores = feature_extractor.calculate_word_bigram_scores(positive_reviews, negative_reviews)

    # 3. Transform review to features by setting labels to words in review
    best_words = feature_extractor.find_best_words(word_scores, 1500)  # Set dimension and initiallize most informative words

    # posFeatures = feature_extractor.pos_features(feature_extractor.bigrams)
    # negFeatures = feature_extractor.neg_features(feature_extractor.bigrams)

    # posFeatures = feature_extractor.pos_features(feature_extractor.bigram_words)
    # negFeatures = feature_extractor.neg_features(feature_extractor.bigram_words)

    # posFeatures = feature_extractor.pos_features(feature_extractor.best_word_features)
    # negFeatures = feature_extractor.neg_features(feature_extractor.best_word_features)

    posFeatures = feature_extractor.set_positive_label(positive_reviews, feature_extractor.best_combined_features, best_words)
    negFeatures = feature_extractor.set_negative_label(negative_reviews, feature_extractor.best_combined_features, best_words)

    # 4. Train classifier and examing classify accuracy
    # Make the feature set ramdon
    shuffle(posFeatures)
    shuffle(negFeatures)

    # 5. After finding the best classifier,store it and then check different dimension classification accuracy
    # 75% of features used as training set (in fact, it have a better way by using cross validation function)
    size_pos = int(len(positive_reviews) * 0.75)
    size_neg = int(len(negative_reviews) * 0.75)

    train_set = posFeatures[:size_pos] + negFeatures[:size_neg]
    test_set = posFeatures[size_pos:] + negFeatures[size_neg:]

    test, tag_test = zip(*test_set)

    classifier = []
    classifier = feature_extractor.cal_classifier_accuracy(train_set, test, tag_test)
    # 选择准确度最高的分类器,正常情况下是选择准确性最高的
    object = feature_extractor.find_best_classifier(classifier)
    print '选择的分类器是：'
    print object
    # 存储分类器
    print '存储分类器'
    feature_extractor.store_classifier(object, train_set, path)
    print '结束训练分类器'
    print '开始预测'
    clf = pickle.load(open(path + '/classifier.pkl'))
    predict = clf.prob_classify_many(feature_extractor.extract_features(test_review, best_words))
    print '存储预测结果'
    feature_extractor.store_predict_result(path, predict)
    print '结束预测'
    end_time = time.time()
    print end_time - start_time
