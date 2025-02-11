python main.py -c paddlex/configs/modules/video_classification/PP-TSM-R50_8frames_uniform.yaml -o Global.mode=train -o Train.num_classes=400 -o Train.batch_size=12 -o Train.epochs_iters=80 -o Train.pretrain_weight_path=https://paddle-model-ecology.bj.bcebos.com/paddlex/data/research_development_data/ResNet50_vd_ssld_v2_pretrained.pdparams  -o Global.device=gpu:0,1,2,3,4,5,6,7 -o Global.dataset_dir=../K400_dataset -o Global.output='./output/video_classification/PP-TSM-R50_8frames_uniform_dy'