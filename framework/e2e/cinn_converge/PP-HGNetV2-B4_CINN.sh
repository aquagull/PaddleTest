python main.py -c paddlex/configs/modules/image_classification/PP-HGNetV2-B4.yaml -o Global.mode=train -o Train.num_classes=1000 -o Train.epochs_iters=200 -o Train.batch_size=64 -o Train.learning_rate=0.5 -o Train.pretrain_weight_path=None -o Global.device=gpu:0,1,2,3,4,5,6,7 -o Global.dataset_dir=../ILSVRC2012/ -o Global.output='./output/image_classification/PP-HGNetV2-B4_CINN' -o Train.dy2st=True