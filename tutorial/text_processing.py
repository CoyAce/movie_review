# coding=utf-8

""" 
Read data from excel file and txt file.
Chinese word segmentation, postagger, sentence cutting and stopwords filtering function.

"""

import xlrd
import jieba
import jieba.posseg
import os

path = os.getcwd()
jieba.load_userdict(path + '/dict/userdict.txt')  # 使用自定义词典，自己抓的所有的电影明星和电影名称


def extract_excel(file_path, nth_sheet):
    table = xlrd.open_workbook(file_path)
    return table.sheets()[nth_sheet - 1]


def extract_txt_of_multiple_line(file_path):
    """
    :param file_path: A txt file with many lines
    :return: every line is a element of the returned list
    """
    file = open(file_path, 'r')
    result = ''.join(file.readlines()).decode('utf8').split('\n')
    file.close()
    return result


def extract_txt_of_one_line(file_path):
    """
    :param file_path: A txt file with only one line of data
    :return: a string
    """
    file = open(file_path, 'r')
    result = file.readline().decode('utf8')
    file.close()
    return result


def segment_to_str(sentence):
    """
    segment sentence to str
    :param sentence: '这款手机大小合适'
    :return: u'\u8fd9 \u6b3e \u624b\u673a \u5927\u5c0f \u5408\u9002'
    """
    segmentation_result = ' '.join(sentence_cut_generator(sentence))
    return segmentation_result


def segment_to_word_list(sentence):
    """
    segment sentence to word list
    :param sentence: '这款手机大小合适'
    :return: [u'\u8fd9', u'\u6b3e', u'\u624b\u673a', u'\u5927\u5c0f', u'\u5408\u9002']
    """
    segmentation_result = []
    for w in sentence_cut_generator(sentence):
        segmentation_result.append(w)
    return segmentation_result


def sentence_cut_generator(sentence):
    return jieba.cut(sentence)


def load_data_and_segment_sentences(file_path, nth_sheet=1, nth_column=1):
    """

    :param file_path: An excel file with product reviews
    :param nth_sheet:by default 1-th sheet
    :param nth_column:by default 1-th column
    :return: A multi-dimension list of reviews, filtered by stopword list.
    """
    # Read product review data from excel file and segment every review
    segmented_review_data = []
    sheet = extract_excel(file_path, nth_sheet)
    for cell in sheet.col_values(nth_column - 1)[0:sheet.nrows]:
        # Segment every review
        segmented_review_data.append(segment_to_word_list(cell))

    # Read txt file contain sentiment stopwords
    sentiment_stopwords = extract_txt_of_multiple_line(path + '/dict/sentiment_stopword.txt')

    # Filter stopwords from reviews
    segmented_and_filtered_reviews = []
    for review in segmented_review_data:
        filtered_review = [word for word in review if word not in sentiment_stopwords and word != ' ']
        segmented_and_filtered_reviews.append(filtered_review)
        filtered_review = []

    # Return filtered segment reviews
    return segmented_and_filtered_reviews
