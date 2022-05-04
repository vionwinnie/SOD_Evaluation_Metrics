"""Custom evalution script"""
import sys
import os
import src.shared.paths as paths

import torch
import torch.nn as nn
import argparse
import os.path as osp
from evaluator import Eval_thread
from dataloader import EvalDataset, EvalBoundaryDataset

# from concurrent.futures import ThreadPoolExecutor
def main(cfg):
    output_dir = cfg.save_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    pred_dir = cfg.pred_root_dir
    is_cuda = cfg.cuda == 'True'
    print(is_cuda)
    print("Prediction directory: {}".format(pred_dir))

    if cfg.methods is None:
        method_names = os.listdir(pred_dir)
    else:
        method_names = cfg.methods.split(' ')
        method_names = [method for method in method_names if method ]
        #method_names = cfg.methods
    if cfg.datasets is None:
        dataset_names = os.listdir(gt_dir)
    else:
        dataset_names = cfg.datasets.split(' ')
        dataset_names = [dataset for dataset in dataset_names if dataset ]
    
    print("all methods:",method_names)
    print("all datasets:",dataset_names)

    threads = []
    for dataset in dataset_names:
        for method in method_names:
            # src/dir - dataset - gt / method
            loader = EvalDataset(osp.join(pred_dir, dataset, method), osp.join(pred_dir, dataset,'masks'))
            edge_loader = EvalBoundaryDataset(osp.join(pred_dir, dataset, method), osp.join(pred_dir, dataset,'masks'))
            thread = Eval_thread(loader, edge_loader, method, dataset, output_dir, is_cuda)
            threads.append(thread)
    for thread in threads:
        print(thread.run())

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--methods', type=str, default="U2-Net")
    parser.add_argument('--datasets', type=str, default="DUTS-TE")
    parser.add_argument('--pred_root_dir', type=str, default=None)
    parser.add_argument('--save_dir', type=str, default='./score/')
    parser.add_argument('--cuda', type=str, default='False')
    config = parser.parse_args()
    main(config)
