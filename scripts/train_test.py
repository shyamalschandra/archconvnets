
import os

def do_extract():
    cmd_tmpl  = """python extractnet.py --gpu=0 --test-range=0-%d --train-range=0 --data-provider=general-cropped --feature-layer=%s --write-disk=1 --feature-path=/export/storage/yamins_skdata/features/%s_%s --data-path=/export/storage/yamins_skdata/%s --load-query='%s' --checkpoint-fs-name=%s --dp-params='{"perm_type": "random", "perm_seed": 0, "preproc": {"normalize": false, "dtype": "float32", "resize_to": %s, "mode": "RGB", "crop": null, "mask": null}, "batch_size": 256, "meta_attribute": "%s", "dataset_name": ["%s", "%s"]}'"""

    layer_names = [
                   #'data',
                   #'conv1_1a', 'conv1_1b', 
                   #'conv2_4a', 'conv2_4b', 
                   #'conv3_7a', 'conv3_7b', 
                   #'conv4_8a', 'conv4_8b', 
                   #'conv5_9a', 'conv5_9b',
                   #'pool1_3a', 'pool1_3b', 
                   #'pool2_6a', 'pool2_6b', 
                   #'pool3_11a', 'pool3_11b',
#                   'fc1_12a', 'fc1_12b', 
#                   'rnorm4_13a', 'rnorm4_13b',
#                   'fc2_14a', 'fc2_14b',  
                   'rnorm5_15a', 'rnorm5_15b'
                   ]
    layer_names = [','.join(layer_names)]


    #dsetmods = ['dldata.stimulus_sets.hvm', 'dldata.stimulus_sets.synthetic.synthetic_datasets']
    #dsetobjs = ['HvMWithDiscfade', 'TrainingDatasetLarge']
    data_paths = [
                   #"hvm_batches_138_permuted", 
                   #"synthetic_batches_large",
                   "imagenet_challenge_138",
 #                  "synthetic_batches_rosch"
                 ]
    resize_tos = [
                  '[138, 138]',
 #                 '[138, 138, 3]'
                  ]

    batch_limits = [
                    50,
                  #  50
                    ]
    dsetmods = [
                'imagenet.dldatasets'
                #'dldata.stimulus_sets.synthetic.synthetic_datasets'
                ]
    dsetobjs = [
                'ChallengeSynsets2013_offline'
                #'RoschDataset'
                ]
    mattrs = [ 'synset'
               # "category",
                ]

    model_names = ["imagenet_trained", 
                   #"synthetic_category_trained", 
                  # "rosch_trained",
                  #, 'imagenet_trained_nofc'
                   ]
    queries = ['{"experiment_data.experiment_id":"imagenet_training_reference_0"}', 
               #'{"experiment_data.experiment_id": "synthetic_training_bsize256_large_category"}', 
               #'{"experiment_data.experiment_id": "synthetic_training_rosch_category"}',
               #'{"experiment_data.experiment_id":"imagenet_training_reference_0_nofc"}',
              ]
    fs_names = ['reference_models', 
                #'convnet_checkpoint_fs', 
                #'convnet_checkpoint_fs',
                #, 'reference_models'
                ]

    vals = [(batch_limit, layer_name, model_name, dsetobj, data_path, query, fs_name, rst, mattr, dsetmod, dsetobj) for batch_limit, data_path, rst, mattr, dsetmod, dsetobj in zip(batch_limits, data_paths, resize_tos, mattrs, dsetmods, dsetobjs) for model_name, query, fs_name in zip(model_names, queries, fs_names) for layer_name in layer_names]

    for val in vals[:]:
        print('VAL', val)
        cmd = cmd_tmpl % val
        os.system(cmd)
        print(cmd)


import filter_analysis
import cPickle
def do_train(outdir):
    model_names = ["imagenet_trained", "synthetic_category_trained", "rosch_trained"]
    layer_names = ['conv1_1a', 'conv1_1b', 'conv2_4a', 'conv2_4b', 'conv3_7a', 'conv3_7b', 'conv4_8a', 'conv4_8b', 'conv5_9a', 'conv5_9b', 'pool3_11a', 'pool3_11b', 'fc1_12a', 'fc1_12b', 'rnorm4_13a', 'rnorm4_13b','fc2_14a', 'fc2_14b',  'rnorm5_15a', 'rnorm5_15b']
    for mname in model_names[2:]:
        for lname in layer_names[:]:
            res = filter_analysis.compute_performance(mname, lname)
            fname = os.path.join(outdir, '%s_%s.pkl' %(mname, lname))
            with open(fname, 'w') as _f:
                cPickle.dump(res, _f)

    model_names = ["imagenet_trained_nofc"]
    layer_names = ['conv1_1a', 'conv1_1b', 'conv2_4a', 'conv2_4b', 'conv3_7a', 'conv3_7b', 'conv4_8a', 'conv4_8b', 'conv5_9a', 'conv5_9b', 'pool3_11a', 'pool3_11b']
    for mname in model_names[:1]:
        for lname in layer_names[:1]:
            res = filter_analysis.compute_performance(mname, lname)
            fname = os.path.join(outdir, '%s_%s.pkl' %(mname, lname))
            with open(fname, 'w') as _f:
                cPickle.dump(res, _f)

if __name__ == '__main__':
    do_extract()
