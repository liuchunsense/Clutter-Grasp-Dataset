# -*- coding: utf-8 -*-
"""
@Time ： 2020/3/23 12:13
@Auth ： 王德鑫
@File label.py
@IDE ：PyCharm
@Function: 三角表示法 标注类文件
"""
import cv2
import glob
import os
import copy
import time
import math
import numpy as np
from skimage.draw import polygon
from skimage.draw import circle as skicircle


class Label:
    def __init__(self):
        # ---------------- 设置宏定义 ---------------- #
        # 设置标记颜色
        self.COLOR_RED = (0, 0, 255)
        self.COLOR_GREEN = (0, 255, 0)
        self.COLOR_BLUE = (255, 255, 0)
        self.COLOR_PINK = (255, 0, 255)
        self.COLOR_LIGHT_BLUE = (255, 0, 0)

        # 键盘按键
        self.KEY_UP = 2490368
        self.KEY_DOWN = 2621440
        self.KEY_LEFT = 2424832
        self.KEY_RIGHT = 2555904
        self.KEY_SPACE = 32
        self.KEY_ESC = 27
        self.KEY_W = 119
        self.KEY_S = 115
        self.KEY_Q = 113
        self.KEY_E = 101

        # 抓取宽度显示状态
        self.GRASP_RED = 1101
        self.GRASP_GREEN = 1102
        self.GRASP_BOTH = 1103
        self.GRASP_CIRCLE = 1104
        self.GRASP_NULL = 0

        # ---------------- 初始化变量 ---------------- #
        self.LABELING_POINTS = False  # 抓取位置标注标志
        self.LABELING_POINTS_WIDTH = False  # 抓取位置标注的宽度 标志
        self.LABELING_GRASP_WIDTH = False  # 抓取宽度设置 标志
        self.LABEL_UPDATE = False  # 更新静态标注图
        self.LABEL_SHOW_ANGLE_CIRCLE = False  # 显示直线两侧的圆
        self.LABEL_SHOW_GRASP_LINE = self.GRASP_NULL  # 显示抓取宽度
        self.LINE_SIDE_POINTS = []

        # 抓取位置标注        [起点x  起点y  终点x 终点y angle1 angle2 线宽  抓取宽度]
        self.LABEL_POINTS = [None, None, None, None, None, None, None, None]

        self.LABEL_POINTS_ALL = []  # 记录每一次标注的信息   [self.LABEL_POINTS]

    def update(self):
        if self.LABEL_POINTS[2] is not None:
            print('>> 已标注', self.LABEL_POINTS)
            self.LABEL_POINTS_ALL.append(self.LABEL_POINTS)  # 更新 LABEL_POINTS_ALL   !!!
            self.LABEL_UPDATE = True

        self.LABELING_POINTS = False  # 抓取位置标注标志
        self.LABELING_POINTS_WIDTH = False  # 抓取位置标注的宽度 标志
        self.LABEL_SHOW_ANGLE_CIRCLE = False  # 显示直线两侧的圆
        self.LABEL_SHOW_GRASP_LINE = self.GRASP_NULL  # 显示抓取宽度
        self.LABEL_POINTS = [None, None, None, None, None, None, None, None]

    def getRectPoints(self, x1, y1, x2, y2, w):
        """
        返回给定矩形内的所有点坐标
        :param x1:直线一端的x坐标
        :param y1:直线一端的y坐标
        :param x2:直线另一端的x坐标
        :param y2:直线另一端的y坐标
        :param w:线宽
        :return:rr, cc 分别是矩形内点的x和y，每个是一维的array
        """
        if x2 == x1:
            angle = math.pi / 2
        else:
            angle = np.arctan((y1 - y2) / (x2 - x1))

        rect = []
        rect.append([y1 - w / 2 * np.cos(angle), x1 - w / 2 * np.sin(angle)])
        rect.append([y2 - w / 2 * np.cos(angle), x2 - w / 2 * np.sin(angle)])
        rect.append([y2 + w / 2 * np.cos(angle), x2 + w / 2 * np.sin(angle)])
        rect.append([y1 + w / 2 * np.cos(angle), x1 + w / 2 * np.sin(angle)])
        rect = np.array(rect)
        return polygon(rect[:, 0], rect[:, 1], (480, 640))

    def getCirclePoints(self, x, y, r):
        """
        返回给定圆内的所有点坐标
        :param x: x
        :param y: y
        :param r: 半径
        :return:
        """
        return skicircle(float(y), float(x), float(r))

    def getLineSidePoint(self):
        """获取标记线两侧圆的中心点"""
        x1 = self.LABEL_POINTS[0]
        y1 = self.LABEL_POINTS[1]
        x2 = self.LABEL_POINTS[2]
        y2 = self.LABEL_POINTS[3]

        length = 20  # 画的球离直线的距离

        cx = (x1 + x2) / 2  # 垂线中心点 x
        cy = (y1 + y2) / 2  # 垂线中心点 y

        if y1 == y2:
            ccx1 = cx
            ccy1 = cy + length
            ccx2 = cx
            ccy2 = cy - length
        else:
            k = (x1 - x2) / (y2 - y1)  # 垂线的斜率
            dx = length / pow(k ** 2 + 1, 0.5)  # l在水平方向的投影长度
            ccx1 = cx + dx
            ccy1 = cy + dx * k
            ccx2 = cx - dx
            ccy2 = cy - dx * k

        self.LINE_SIDE_POINTS.clear()
        self.LINE_SIDE_POINTS.append([ccx1, ccy1])
        self.LINE_SIDE_POINTS.append([ccx2, ccy2])

    def writelabel(self, filename):
        """
        创建并写入标签文件
        :param filename:[../01/pcd0***Label1.txt, ../01/pcd0***Label2.txt]
        """
        # 根据端点和线宽获取线上的点
        # 获取的点是(x, y)，要替换成(row, col)
        label_points = None
        for label_line in self.LABEL_POINTS_ALL:
            x1 = label_line[0]
            y1 = label_line[1]
            x2 = label_line[2]
            y2 = label_line[3]
            angle1 = label_line[4]
            angle2 = label_line[5]
            w = label_line[6]  # 对直线来说是线宽，对圆形来说是直径
            grasp_w = label_line[7]     # 抓取宽度

            # 如果起点和终点相同，表示当前标注的是球形抓取，根据圆形来获取抓取点坐标
            if x1 == x2 and y1 == y2:
                rr, cc = self.getCirclePoints(x1, y1, w/2)
            else:  # 根据矩形获取抓取点
                rr, cc = self.getRectPoints(x1, y1, x2, y2, w)

            rows = rr.reshape((-1, 1))  # row
            cols = cc.reshape((-1, 1))  # col

            if angle1 is None:      # angle1
                angles1 = [['None'] for _ in range(rows.shape[0])]
                angles1 = np.array(angles1)
            else:
                angles1 = np.zeros(rows.shape)
                angles1[:, :] = angle1

            if angle2 is None:      # angle2
                angles2 = [['None'] for _ in range(rows.shape[0])]
                angles2 = np.array(angles2)
            else:
                angles2 = np.zeros(rows.shape)
                angles2[:, :] = angle2

            # 获取抓取宽度
            ws = np.zeros(rows.shape)
            ws[:, :] = grasp_w * 2      # grasp_w是抓取点一侧的宽度

            points = np.hstack((rows, cols, angles1, angles2, ws))  # 横向合并坐标点标注信息
            if label_points is None:
                label_points = points
            else:
                label_points = np.vstack((label_points, points))

        # label_points 为二维array，每一行为一个点，数据分别是 row, col, ...
        # 方案1
        with open(filename, 'w', encoding="utf-8") as f:
            for idx in range(label_points.shape[0]):
                point = label_points[idx]
                for item in point:
                    if item != 'None':
                        f.write('{} '.format(item))
                f.write('\n')


    def angle(self, pt1, pt2):
        """
        计算pt1到pt2连线与水平轴的夹角[0, 2π]
        :param pt1: 起点[x, y]
        :param pt2: 终点[x, y]
        :return:
        """
        dx = pt2[0] - pt1[0]
        dy = pt1[1] - pt2[1]    # math.atan2是在正常的坐标系中计算角的
        angle = math.atan2(dy, dx)
        if angle < 0:
            angle += 2 * math.pi
        return angle

    def key_monitor(self, key):
        """键盘监听"""
        # 下一张
        if key == self.KEY_SPACE:
            self.update()  # 初始化标志位并更新标注数据

        # 停止标注
        elif key == 27:
            self.update()  # 初始化标志位并更新标注数据

        # 上 下 调整线宽
        elif key in [self.KEY_UP, self.KEY_DOWN]:
            if self.LABEL_POINTS[6] is None:
                return
            self.LABEL_POINTS[6] -= int(key / 2621440) * 2 - 1  # 设置抓取位置标注 线宽
            self.LABEL_POINTS[6] = max(1, int(self.LABEL_POINTS[6]))
            print('\r>> 线宽 {}'.format(self.LABEL_POINTS[6])) 
            self.LABELING_POINTS_WIDTH = True

        # 左 右 调整抓取宽度
        elif key in [self.KEY_LEFT, self.KEY_RIGHT]:
            if self.LABEL_POINTS[7] is None:
                return
            self.LABEL_POINTS[7] -= int(key / 2555904) * 4 - 2  # 设置抓取宽度
            self.LABEL_POINTS[7] = max(6, int(self.LABEL_POINTS[7]))       # 抓取宽度不小于10 抓取点一侧的宽度
            
        # 区分抓取方向
        # W对应红色点 LINE_SIDE_POINTS[1], S对应绿色点 LINE_SIDE_POINTS[0]， Q对应球形抓取，E对应对称抓取
        elif key in [self.KEY_W, self.KEY_S, self.KEY_Q, self.KEY_E]:  # W S Q E
            if key == self.KEY_W:
                # print('>> W')
                # 计算从标注线中心点到 LINE_SIDE_POINTS[1]的角
                x1 = (self.LABEL_POINTS[0] + self.LABEL_POINTS[2]) / 2  # 标注线中心点 x
                y1 = (self.LABEL_POINTS[1] + self.LABEL_POINTS[3]) / 2  # 标注线中心点 y

                x2 = self.LINE_SIDE_POINTS[1][0]
                y2 = self.LINE_SIDE_POINTS[1][1]

                self.LABEL_POINTS[4] = self.angle([x1, y1], [x2, y2])
                self.LABEL_POINTS[5] = None
                self.LABEL_SHOW_GRASP_LINE = self.GRASP_RED
                print('>> 抓取角 ', self.LABEL_POINTS[4] / math.pi * 180)

            elif key == self.KEY_S:
                # print('>> S')
                # 计算从标注线中心点到 LINE_SIDE_POINTS[0]的角
                x1 = (self.LABEL_POINTS[0] + self.LABEL_POINTS[2]) / 2  # 标注线中心点 x
                y1 = (self.LABEL_POINTS[1] + self.LABEL_POINTS[3]) / 2  # 标注线中心点 y

                x2 = self.LINE_SIDE_POINTS[0][0]
                y2 = self.LINE_SIDE_POINTS[0][1]

                self.LABEL_POINTS[4] = self.angle([x1, y1], [x2, y2])
                self.LABEL_POINTS[5] = None
                self.LABEL_SHOW_GRASP_LINE = self.GRASP_GREEN
                print('>> 抓取角 ', self.LABEL_POINTS[4] / math.pi * 180)

            elif key == self.KEY_Q:
                # print('>> Q')
                self.LABEL_POINTS[4] = None
                self.LABEL_POINTS[5] = None
                self.LABEL_SHOW_GRASP_LINE = self.GRASP_CIRCLE
                print('>> 抓取角 [0, 2π]')
                # pass

            elif key == self.KEY_E:
                # print('>> E')
                # 计算从标注线中心点到 LINE_SIDE_POINTS[1]的角
                x1 = (self.LABEL_POINTS[0] + self.LABEL_POINTS[2]) / 2  # 标注线中心点 x
                y1 = (self.LABEL_POINTS[1] + self.LABEL_POINTS[3]) / 2  # 标注线中心点 y

                x2 = self.LINE_SIDE_POINTS[1][0]
                y2 = self.LINE_SIDE_POINTS[1][1]

                self.LABEL_POINTS[4] = self.angle([x1, y1], [x2, y2])

                # 计算从标注线中心点到 LINE_SIDE_POINTS[0]的角
                x1 = (self.LABEL_POINTS[0] + self.LABEL_POINTS[2]) / 2  # 标注线中心点 x
                y1 = (self.LABEL_POINTS[1] + self.LABEL_POINTS[3]) / 2  # 标注线中心点 y

                x2 = self.LINE_SIDE_POINTS[0][0]
                y2 = self.LINE_SIDE_POINTS[0][1]

                self.LABEL_POINTS[5] = self.angle([x1, y1], [x2, y2])

                self.LABEL_SHOW_GRASP_LINE = self.GRASP_BOTH
                print('>> 抓取角 ', self.LABEL_POINTS[4] / math.pi * 180, self.LABEL_POINTS[5] / math.pi * 180)

            self.LABEL_POINTS[7] = 20   # 初始化抓取宽度



