from torch.utils import data
import torch
import os
from PIL import Image
from scipy import ndimage
import cv2
import numpy as np
from scipy.ndimage import distance_transform_edt
from skimage.morphology import erosion, disk

def boundary_extraction(mask):
    """
    Function cited by the author in this Github issue: https://github.com/xuebinqin/BASNet/issues/20
    """ 
    (h,w) = mask.shape
    mask_pad = np.zeros((h+10,w+10))
    mask_pad[5:h+5,5:w+5] = mask

    mask_pad_erd = erosion(mask_pad,disk(1))
    mask_pad_edge = np.logical_xor(mask_pad, mask_pad_erd)

    return mask_pad_edge[5:h+5,5:w+5]

class EvalDataset(data.Dataset):
    def __init__(self, img_root, label_root):
        lst_label = sorted(os.listdir(label_root))
        lst_pred = sorted(os.listdir(img_root))
        lst = []
        for name in lst_label:
            if name in lst_pred:
                lst.append(name)

        self.lst = lst
        self.image_path = list(map(lambda x: os.path.join(img_root, x), lst))
        self.label_path = list(map(lambda x: os.path.join(label_root, x), lst))

    def __getitem__(self, item):
        pred = Image.open(self.image_path[item]).convert('L')
        gt = Image.open(self.label_path[item]).convert('L')

        if pred.size != gt.size:
            pred = pred.resize(gt.size, Image.BILINEAR)
        img_name = self.lst[item]

        return pred, gt, img_name

    def __len__(self):
        return len(self.image_path)

class EvalBoundaryDataset(data.Dataset):
    def __init__(self, img_root, label_root):
        lst_label = sorted(os.listdir(label_root))
        lst_pred = sorted(os.listdir(img_root))
        lst = []
        for name in lst_label:
            if name in lst_pred:
                lst.append(name)

        self.lst = lst
        self.image_path = list(map(lambda x: os.path.join(img_root, x), lst))
        self.label_path = list(map(lambda x: os.path.join(label_root, x), lst))

    def __getitem__(self, item):
        pred = cv2.imread(self.image_path[item],0)
        gt = cv2.imread(self.label_path[item],0)

        if pred.size != gt.size:
            pred = pred.resize(gt.size, Image.BILINEAR)

        # Dark pixel = 0, Bright pixels = 1
	# Note: by experimentation, clipping at 127 works better
        #gt[gt <= 2*np.mean(gt)] = 0
        #gt[gt > 2*np.mean(gt)] = 1
	gt[gt <= 127] = 0
	gt[gt > 127] = 1

        pred[pred <= 127] = 0
        pred[pred > 127] = 1

        pred_edge = boundary_extraction(pred)
        gt_edge = boundary_extraction(gt)
        
        pred_dist = distance_transform_edt(np.logical_not(pred_edge))
        gt_dist = distance_transform_edt(np.logical_not(gt_edge))

        img_name = self.lst[item]

        return pred_edge, gt_edge, pred_dist, gt_dist, img_name

    def __len__(self):
        return len(self.image_path)
