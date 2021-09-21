"""
创建训练和测试列表
"""

import os
import glob
import shutil 

path = 'E:/research/dataset/grasp/cornell/wdx_sgdn_new/img_my_single'

rgb_files = glob.glob(os.path.join(path, '*r.png'))
rgb_files.sort()

i = 0
for rgb_file in rgb_files:
    # if i % 3 == 0:
    #     pass
    # else:
    print(os.path.basename(rgb_file)[:7])
    i += 1