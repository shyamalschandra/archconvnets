import time
import numpy as np
from archconvnets.unsupervised.pool_inds_py import max_pool_locs
#from archconvnets.unsupervised.pool_inds_py import max_pool_locs
from archconvnets.unsupervised.conv import conv_block
#from archconvnets.unsupervised.cudnn_module.cudnn_module import *
#from archconvnets.unsupervised.scaled.compute_sigma31_reduced import s31

from archconvnets.unsupervised.scaled.compute_sigma31 import s31

import archconvnets.unsupervised.sigma31_layers.sigma31_layers as sigma31_layers

from scipy.io import savemat, loadmat
from scipy.stats import zscore

conv_block_cuda = conv_block
F1_scale = 0.01 # std of init normal distribution
F2_scale = 0.01
F3_scale = 0.01
FL_scale = 0.3

POOL_SZ = 3
POOL_STRIDE = 2
STRIDE1 = 1 # layer 1 stride
N_IMGS = 10000 # batch size
IMG_SZ_CROP = 32 # input image size (px)
IMG_SZ = 32 # input image size (px)
img_train_offset = 0
PAD = 3

N = 8
n1 = N # L1 filters
n2 = N
n3 = N

s1 = 5
s2 = 5
s3 = 3

N_C = 10 # number of categories

output_sz1 = len(range(0, (IMG_SZ+2*PAD) - s1 + 1, STRIDE1))
max_output_sz1  = len(range(0, output_sz1-POOL_SZ, POOL_STRIDE)) + 2*PAD

output_sz2 = max_output_sz1 - s2 + 1
max_output_sz2  = len(range(0, output_sz2-POOL_SZ, POOL_STRIDE)) + 2*PAD

np.random.seed(6666)
F1 = np.single(np.random.normal(scale=F1_scale, size=(n1, 3, s1, s1)))
F2 = np.single(np.random.normal(scale=F2_scale, size=(n2, n1, s2, s2)))
F3 = np.single(np.random.normal(scale=F3_scale, size=(n3, n2, s3, s3)))

F1 = zscore(F1,axis=None)/500
F2 = zscore(F2,axis=None)/500
F3 = zscore(F3,axis=None)/500

imgs_mean = np.load('/home/darren/cifar-10-py-colmajor/batches.meta')['data_mean']
for batch in range(1,6):
	z = np.load('/home/darren/cifar-10-py-colmajor/data_batch_' + str(batch))

	################### compute train err
	# load imgs
	x = z['data'] - imgs_mean
	x = x.reshape((3, 32, 32, 10000))
	imgs_pad = np.zeros((3, IMG_SZ+2*PAD, IMG_SZ+2*PAD, N_IMGS),dtype='single')
	imgs_pad[:,PAD:PAD+IMG_SZ_CROP,PAD:PAD+IMG_SZ_CROP] = x[:,:,:,:N_IMGS]
	imgs_pad = np.ascontiguousarray(imgs_pad.transpose((3,0,1,2)))

	labels = np.asarray(z['labels'])[:N_IMGS].astype(int)

	# forward pass
	t_forward_start = time.time()
	#conv_output1 = conv_block_cuda(F1, imgs_pad)
	conv_output1 = conv_block_cuda(np.double(F1.transpose((1,2,3,0))), np.double(imgs_pad.transpose((1,2,3,0)))).transpose((3,0,1,2))
	max_output1t, output_switches1_x, output_switches1_y = max_pool_locs(np.single(conv_output1))

	#max_output1 = max_output1t
	max_output1 = np.zeros((N_IMGS, n1, max_output_sz1, max_output_sz1),dtype='single')
	max_output1[:,:,PAD:max_output_sz1-PAD,PAD:max_output_sz1-PAD] = max_output1t

	#conv_output2 = conv_block_cuda(F2, max_output1)
	conv_output2 = conv_block_cuda(np.double(F2.transpose((1,2,3,0))), np.double(max_output1.transpose((1,2,3,0)))).transpose((3,0,1,2))
	max_output2t, output_switches2_x, output_switches2_y = max_pool_locs(np.single(conv_output2), PAD=PAD)

	max_output2 = np.zeros((N_IMGS, n2, max_output_sz2, max_output_sz2),dtype='single')
	max_output2[:,:,PAD:max_output_sz2-PAD,PAD:max_output_sz2-PAD] = max_output2t

	conv_output3 = conv_block_cuda(np.double(F3.transpose((1,2,3,0))), np.double(max_output2.transpose((1,2,3,0)))).transpose((3,0,1,2))
	max_output3t, output_switches3_x, output_switches3_y = max_pool_locs(np.single(conv_output3), PAD=PAD)

	output_switches2_x -= PAD
	output_switches2_y -= PAD

	output_switches3_x -= PAD
	output_switches3_y -= PAD

	sigma31 = sigma31_layers.s31_full_gpu(output_switches3_x, output_switches3_y, output_switches2_x, output_switches2_y, output_switches1_x, output_switches1_y, s1, s2, s3, labels, imgs_pad, N_C)
	print time.time() - t_forward_start

	np.save('/home/darren/sigma31_8_crop_' + str(batch) + '.npy', sigma31)

'''sigma31_F1 = sigma31*F1.reshape((1, n1, 3, s1, s1,  1, 1, 1, 1, 1,1,1,1))
sigma31_F2 = sigma31_F1*F2.transpose((1,0,2,3)).reshape((1, n1, 1, 1, 1, n2, s2, s2, 1, 1,1,1,1))
sigma31_F3 = sigma31_F2*F3.transpose((1,0,2,3)).reshape((1, 1, 1, 1, 1, n2, 1, 1, n3, s3, s3, 1, 1))

sigma31_F3 = sigma31_F3[6].reshape((n1*3*(s1**2)*n2*(s2**2), n3, s3**2, 5, 5)).sum(0).sum(1)[np.newaxis]

print np.isclose(sigma31_F3, max_output3t[0][np.newaxis]).sum() / np.single(np.prod(sigma31_F3.shape))'''

