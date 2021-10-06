# Clutter-Grasp-Dataset

## AFFGA-Net

The AFFGA-Net is a high performance network which predicts the quality and pose of grasps at every pixel in an input RGB image. 

This repository contains the data set used to train AFFGA-Net and the program for labeling the grasp model.



**High-performance Pixel-level Grasp Detection based on Adaptive Grasping and Grasp-aware Network**

Dexin Wang, Chunsheng Liu, Faliang Chang, Nanjun Li, Guangxin Li

This paper has been accepted by *IEEE Trans. Ind. Electron*.

[TechRxiv](https://www.techrxiv.org/articles/preprint/High-performance_Pixel-level_Grasp_Detection_based_on_Adaptive_Grasping_and_Grasp-aware_Network/14680455) | [Video](https://youtu.be/ccA1jkkbBJA)



## 1 dataset

The dataset is publiced on https://drive.google.com/drive/folders/1knXlR72Z_5OcE9_lVfTz-QOZRhtWB_Yj?usp=sharing.

### 1.1 clutter

The clutter dataset includes 505 images, each image includes one or more objects, and all images are taken with kinect v2 camera.

The zip file contains two kinds of files：`pcd*Label.txt`, `pcd*r.png`.

**`pcd*Label.txt`**：Use `main_label.py` to label the image and generate the file. Each line represents a grasp point, grasp angles and grasp width of an OAR-model.

The grasp point is composed of y and x.

The grasp angles is composed of `0/1/2` angle values. When formula (5) is satisfied, the grasp angles contains `0` angle values, When formula (3) is satisfied, the grasp angles contains `1` angle values, When formula (4) is satisfied, the grasp angles contains `2` angle values, and their difference is $\pi$.

The grasp width is a value in pixels.

For example：

```
the grasp angles contains `0` angle values:
269 274 76.0	
the grasp angles contains `1` angle values:
250 291 4.607512041654457 32.0
the grasp angles contains `2` angle values:
255.0 286.0 3.0309354324158964 6.1725280860056895 52.0
```

**`pcd*r.png`**：The color image corresponding to `pcd*Label.txt`.



### 1.2 cornell

The zip file contains two kinds of files：`pcd*Label.txt`, `pcd*r.png`.

The format of files is the same as `clutter.zip`.



### 1.3 train-test.zip

The zip file contains four folders：train-test-all、train-test-cornell、train-test-mutil、train-test-single.

They save the test set and train set allocation when using the following four types of samples for training:

```
all: Use all samples of clutter and cornell data sets for training
cornell: Only use samples from the cornell dataset
mutil： Only use samples containing multiple objects
single：Only use samples containing single object
```

Each folder contains some of the following files, in which the indexes of test samples and training samples are stored:

```
all-wise-test.txt：Randomly select 20% of all samples as the test set
all-wise-train.txt：Randomly select 80% of all samples as the training set
image-wise-test.txt：Select 20% of the samples as the test set according to image-wise splitting
image-wise-train.txt：Select remaining 80% as the test set
object-wise-test.txt：Select 20% of the samples as the test set according to object-wise splitting
object-wise-train.txt：Select remaining 80% as the test set
```

Please refer to the paper for the explanation of `image-wise splitting` and `object-wise splitting`.

The samples of the test set and training set are randomly generated by the program.



## 2 label your images

1. Modify the `path` on line 73 of `main_label.py` to your image path.
2. run `main_label.py`, the labeling instructions are contained in the file。The `pcd*Label.txt` file will be automatically saved under `path`.
3. Modify `label_path` in `generate_grasp_mat.py` to your image path, and modify `save_path` to a custom path.
4. run `generate_grasp_mat.py`，convert `pcd*Label.txt` to `pcd*grasp.mat`, they represent the same label, but the format is different, which is convenient for AFFGA-Net to read。`pcd*grasp.mat` will be automatically saved under `save_path`.

For the source code of AFFGA-Net, please visit https://github.com/liuchunsense/AFFGA-Net.

Any questions or comments contact Wang Dexin (dexinwang@mail.sdu.edu.cn)
