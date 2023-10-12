# main
import os

import cv2  # >>> pip install opencv-python # cv2
import pytesseract
import numpy as np
import calculate_similarity as calcsim

# import pandas as pd

# 配置Tesseract的路径 https://github.com/tesseract-ocr/tessdoc
# download https://github.com/UB-Mannheim/tesseract/wiki   Tesseract installer for Windows
pytesseract.pytesseract.tesseract_cmd = r'D:\\environments\\Tesseract-OCR\\tesseract.exe'  # 请根据您的设置调整此路径

# 指定目录路径
# directory_path = r'D:\datas\火车头采集\datas\666\page\2023\10'
directory_path = r'img_ori'
# 输出文件路径
output_path = 'img_new'
# 新水印路径
new_watermark_path = 'logo.png'
# 要识别的文字
find_text = 'GITHUB21888'
# 要识别的文字最低相似度,该值越小水印越大
find_text_similarity = 0.75
# 图片压缩
new_img_quality = 80  # 0-100 数字越大图片质量越高
# 水印剩余位置长宽比,这只是识别文字,文字上面下面左边右边如果有图案 可以根据这个参数调整新水印大小位置进行覆盖,
#   假设水印文字上方有个图案 宽400高100 那么填4 新水印就会x1y1就会走到这个图案的x1y1处,适配好长宽一样的图片就可以完美覆盖全部
ResidualPositionRatio = 4

# 失败的文件
file_failed = []

if __name__ == '__main__':
    # 遍历目录中的所有文件
    for filename in os.listdir(directory_path):
        # 拼接完整的文件路径
        full_path = os.path.join(directory_path, filename)
        # 读取图片
        image = cv2.imdecode(np.fromfile(full_path, dtype=np.uint8), -1)  # 采用支持中文的库读入内存，再从内存中进行转换。
        # 读取图片
        # image = cv2.imread(full_path)

        # 使用Tesseract进行OCR，并获取详细数据
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DATAFRAME)

        # 过滤得到包含 '水印文字' 的行
        # find_text_rows = data[data['text'] == find_text]
        find_text_rows = data[
            data['text'].apply(lambda x: calcsim.calculate_similarity(x, find_text)) > find_text_similarity]

        # 相似度80

        # 如果找到了 '水印文字'
        if not find_text_rows.empty:
            # 获取 '水印文字' 的坐标和尺寸（这里假设只有一个 '水印文字'，所以用了iloc[0]）
            x = int(find_text_rows.iloc[0]['left'])
            y = int(find_text_rows.iloc[0]['top'])
            w = int(find_text_rows.iloc[0]['width'])
            h = int(find_text_rows.iloc[0]['height'])
            # 扩大水印区域
            w = int(w * 1.2)
            # 处理相似度导致的尺寸变化
            x = x - int((int(w / find_text_similarity) - w) / 2)
            w = int(w / find_text_similarity)
            # 设置偏移位置
            y = y - int(w / ResidualPositionRatio)
            # 读取需要覆盖的图片
            overlay_image = cv2.imread(new_watermark_path)
            overlay_h, overlay_w, _ = overlay_image.shape

            # 等比缩放覆盖图片的高度，宽度保持与 '水印文字' 一样
            scale_factor = w / overlay_w
            new_h = int(overlay_h * scale_factor)
            new_w = w * 1  # 宽度保持不变

            # print(
            #     "watermark word: x:", x, "y:", y, "w:", w, "h:", h,
            #     ">>> new: new_w:", new_w, "new_h:", new_h
            # )
            resized_overlay = cv2.resize(overlay_image, (new_w, new_h))
            # 添加覆盖图片
            for i in range(min(new_h, image.shape[0] - y)):
                for j in range(min(new_w, image.shape[1] - x)):
                    if resized_overlay[i, j][2] != 0:  # Assuming the blue channel is not zero
                        image[y + i, x + j] = resized_overlay[i, j]

            # 保存或显示结果图片
            # 拼接完整的文件路径
            file_path = os.path.join(output_path, filename)
            # 压缩图片

            # cv2.imwrite(file_path, image)
            # 解决中文路径问题
            cv2.imencode('.jpg', image, [int(cv2.IMWRITE_JPEG_QUALITY), int(new_img_quality)])[1].tofile(file_path)
            print("watermark word added to image:", file_path)
        else:
            # 失败的添加到file_failed
            file_failed.append(filename)
            print("watermark word not found in image.")

    # file_failed 是否有失败的
    if len(file_failed) > 0:
        print("以下图片未处理成功:\r\n", "\r\n".join(file_failed))
