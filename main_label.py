# -*- coding: utf-8 -*-
"""
@Time ： 2020/3/22 16:50
@Auth ： 王德鑫
@File ：main_label.py
@IDE ：PyCharm
@Function: 三角表示法标注执行文件 class
"""

import cv2
import glob
import os
import copy
import math
from label import Label
import time
import tool
import numpy as np
from skimage.draw import polygon
from skimage.draw import circle as skicircle

"""
****** 操作说明 ******
1 用鼠标左键画出一条适合夹持器抓取的直线 

2 按 上/下 调整线宽(抓取区域宽度)
    上: 增加线宽
    下: 减小线宽

3 按 W/S/Q/E 设置抓取模式：
    w: 朝向红色点单向抓取
    S: 朝向绿色单向抓取
    E: 对称抓取
    Q: 圆形抓取

4 按 左/右 调整抓取宽度 (抓取宽度比物体宽2cm，两侧各1cm)
    左: 增加
    右: 减小

换下一张：空格
退出标注：Esc

在换下一张时，当前图像上标注的数据会保存至pcd****label.txt, 
退出时，当前图像的标注不保存
"""

ESC = False     # 标注停止标志


def mouse_monitor(event, x, y, flags, param):
    """鼠标监听"""
    if event == cv2.EVENT_LBUTTONDOWN:  # 按下左键
        label.update()     # 初始化标志位并更新标注数据
        print('>> 抓取位置标注 ... ')
        label.LABEL_POINTS[0] = x     # 设置抓取位置标注 起点
        label.LABEL_POINTS[1] = y
        label.LABEL_POINTS[6] = 1

    elif event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON:      # 左键拖动
        label.LABEL_POINTS[2] = x  # 设置抓取位置标注 终点
        label.LABEL_POINTS[3] = y
        label.LABELING_POINTS = True

    elif event == cv2.EVENT_LBUTTONUP:      # 抬起右键
        # print('>> 抓取位置标注 结束')
        label.LABEL_POINTS[2] = x     # 设置抓取位置标注 终点
        label.LABEL_POINTS[3] = y
        label.LABELING_POINTS = False
        label.LABEL_SHOW_ANGLE_CIRCLE = True


if __name__ == '__main__':
    path = 'E:/research/dataset/grasp/cornell/img' # 数据集图片路径
    label_win_name = 'labeling'
    files = glob.glob(os.path.join(path, 'pcd*[0-9]r.png'))   # 匹配所有的符合条件的文件，并将其以list的形式返回
    files.sort()

    cv2.namedWindow(label_win_name)
    cv2.setMouseCallback(label_win_name, mouse_monitor)

    n = 0   # 记录当前标注个数
    # 依次标注
    for file in files:
        n += 1

        # 可视化深度图
        # depth_file = file.replace('r.png', 'd.png')
        # if os.path.exists(depth_file):
        #     im_depth = cv2.imread(depth_file, -1)
        #     im_depth = tool.crop(im_depth, 400, 400)
        #     im_depth = tool.inpaint(im_depth)
        #     cv2.imshow('depth', tool.depth2Gray(im_depth))

        # 标签文件名
        label_file = file.replace('r.png', 'Label.txt')
        # 跳过已经标注的文件
        if os.path.exists(label_file):
            continue
            
        label_file = label_file.replace('data_1', 'data_new')
        if os.path.exists(label_file):
            continue

        # png_file = file.replace('.txt', 'r.png')    # RGB图像文件名
        png_file = file    # RGB图像文件名
        print('= '*50)
        print('正在标注... {}   {}/{}'.format(png_file, n, len(files)))

        png = cv2.imread(png_file)
        png_visual_static = copy.deepcopy(png)        # 静态可视化的图像
        png_visual_dynamic = copy.deepcopy(png)        # 动态可视化的图像

        cv2.imshow(label_win_name, png_visual_dynamic)  # 显示动态标注图

        label = Label()
        while 1:
            # cv2.imshow(win_name, png)
            # 标注可视化
            if label.LABEL_UPDATE:
                if len(label.LABEL_POINTS_ALL):
                    # 更新静态标注图
                    if label.LABEL_POINTS[0] == label.LABEL_POINTS[2] and label.LABEL_POINTS[1] == label.LABEL_POINTS[3]:  # 标注的是球形
                        cv2.circle(png_visual_static, (label.LABEL_POINTS_ALL[-1][0], label.LABEL_POINTS_ALL[-1][1]),
                                   label.LABEL_POINTS_ALL[-1][6], label.COLOR_BLUE, -1)
                    else:   # 标注的是矩形
                        cv2.line(png_visual_static, (label.LABEL_POINTS_ALL[-1][0], label.LABEL_POINTS_ALL[-1][1]),
                                 (label.LABEL_POINTS_ALL[-1][2], label.LABEL_POINTS_ALL[-1][3]),
                                 label.COLOR_BLUE, label.LABEL_POINTS_ALL[-1][6])
                    label.LABEL_UPDATE = False

            # 动态显示标注情况
            if label.LABELING_POINTS or label.LABELING_POINTS_WIDTH or label.LABEL_SHOW_ANGLE_CIRCLE or label.LABEL_SHOW_GRASP_LINE:
                png_visual_dynamic = copy.deepcopy(png_visual_static)   # 将标注好的图案更新到动态图像上
                if label.LABEL_POINTS[0] == label.LABEL_POINTS[2] and label.LABEL_POINTS[1] == label.LABEL_POINTS[3]:   # 标注的是球形
                    cv2.circle(png_visual_dynamic, (label.LABEL_POINTS[0], label.LABEL_POINTS[1]),
                               int(label.LABEL_POINTS[6] / 2), label.COLOR_BLUE, -1)
                    # 显示标记点外的圆框
                    if label.LABEL_SHOW_ANGLE_CIRCLE:
                        cv2.circle(png_visual_dynamic, (label.LABEL_POINTS[0], label.LABEL_POINTS[1]), 20, label.COLOR_RED, 1)

                else:   # 标注的是矩形
                    cv2.line(png_visual_dynamic, (label.LABEL_POINTS[0], label.LABEL_POINTS[1]),
                             (label.LABEL_POINTS[2], label.LABEL_POINTS[3]),
                             label.COLOR_BLUE, label.LABEL_POINTS[6])
                    # 显示标记线两侧的圆
                    if label.LABEL_SHOW_ANGLE_CIRCLE:
                        # 获取线两侧圆球的坐标
                        label.getLineSidePoint()
                        # LINE_SIDE_POINTS[0]对应绿色点，LINE_SIDE_POINTS[1]对应红色点
                        cv2.circle(png_visual_dynamic, (int(label.LINE_SIDE_POINTS[0][0]), int(label.LINE_SIDE_POINTS[0][1])), 5, label.COLOR_GREEN, -1)      # 注意颜色
                        cv2.circle(png_visual_dynamic, (int(label.LINE_SIDE_POINTS[1][0]), int(label.LINE_SIDE_POINTS[1][1])), 5, label.COLOR_RED, -1)        # 注意颜色

                # 显示抓取宽度
                if label.LABEL_SHOW_GRASP_LINE:
                    cx = int((label.LABEL_POINTS[0] + label.LABEL_POINTS[2]) / 2)  # 垂线中心点 x
                    cy = int((label.LABEL_POINTS[1] + label.LABEL_POINTS[3]) / 2)  # 垂线中心点 y
                    if label.LABEL_SHOW_GRASP_LINE in [label.GRASP_RED, label.GRASP_GREEN]:
                        # 画一边
                        angle = label.LABEL_POINTS[4]
                        k = math.tan(angle)

                        if k == 0:
                            dx = label.LABEL_POINTS[7]
                            dy = 0
                        else:
                            dx = k / abs(k) * label.LABEL_POINTS[7] / pow(k ** 2 + 1, 0.5)
                            dy = k * dx

                        if angle < math.pi:
                            cv2.line(png_visual_dynamic, (cx, cy), (int(cx + dx), int(cy - dy)), label.COLOR_LIGHT_BLUE, 1)
                        else:
                            cv2.line(png_visual_dynamic, (cx, cy), (int(cx - dx), int(cy + dy)), label.COLOR_LIGHT_BLUE, 1)

                    elif label.LABEL_SHOW_GRASP_LINE == label.GRASP_BOTH:
                        # 画两边
                        angle1 = label.LABEL_POINTS[4]
                        angle2 = label.LABEL_POINTS[5]
                        k = math.tan(angle1)

                        if k == 0:
                            dx = label.LABEL_POINTS[7]
                            dy = 0
                        else:
                            dx = k / abs(k) * label.LABEL_POINTS[7] / pow(k ** 2 + 1, 0.5)
                            dy = k * dx

                        if angle1 < math.pi:
                            cv2.line(png_visual_dynamic, (cx, cy), (int(cx + dx), int(cy - dy)), label.COLOR_LIGHT_BLUE, 1)
                        else:
                            cv2.line(png_visual_dynamic, (cx, cy), (int(cx - dx), int(cy + dy)), label.COLOR_LIGHT_BLUE, 1)

                        if angle2 < math.pi:
                            cv2.line(png_visual_dynamic, (cx, cy), (int(cx + dx), int(cy - dy)), label.COLOR_LIGHT_BLUE, 1)
                        else:
                            cv2.line(png_visual_dynamic, (cx, cy), (int(cx - dx), int(cy + dy)), label.COLOR_LIGHT_BLUE, 1)

                    elif label.LABEL_SHOW_GRASP_LINE == label.GRASP_CIRCLE:
                        # 画圆形
                        cv2.circle(png_visual_dynamic, (cx, cy), label.LABEL_POINTS[7], label.COLOR_LIGHT_BLUE, 1)

                label.LABELING_POINTS_WIDTH = False

                cv2.imshow(label_win_name, png_visual_dynamic)      # 显示动态标注图

            # 显示
            cv2.imshow('labeled', png_visual_static)

            # 监听键盘按键
            k = cv2.waitKeyEx(10)
            label.key_monitor(k)
            if k == label.KEY_SPACE:
                # 创建标签文件并写入
                label.writelabel(label_file)
                break
            elif k == label.KEY_ESC:
                ESC = True
                break

        # 停止标注
        if ESC:
            break

    print('标注结束！')
