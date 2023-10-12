# import
import pandas as pd
import Levenshtein


# 定义函数计算Levenshtein相似度
def calculate_similarity(str1, str2):
    if pd.isnull(str1) or pd.isnull(str2):
        return 0
    return Levenshtein.ratio(str1, str2)


def calculate_similarity_test():
    # 模拟从Tesseract获取到的DataFrame
    data = pd.DataFrame({
        'block_num': [1, 1, 1, 1, 2, 2, 2, 2],
        'text': ['这是', '一个', '测试', '文字', '这是', '一个', '水印文字', '示例']
    })

    # 想要查找的文本
    find_text = '水印文字.'
    # 计算每一行文本与find_text的相似度
    data['similarity'] = data['text'].apply(lambda x: calculate_similarity(x, find_text))

    # 过滤出相似度大于0.8的行
    filtered_rows = data[data['similarity'] > 0.8]
    print(filtered_rows)

#
# if __name__ == '__main__':
#     calculate_similarity_test()
