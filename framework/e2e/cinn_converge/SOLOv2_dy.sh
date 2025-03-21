python main.py -c paddlex/configs/modules/instance_segmentation/SOLOv2.yaml \
    -o Global.mode=train -o Global.dataset_dir=../coco \
    -o Train.num_classes=80 -o Train.epochs_iters=12 -o Train.batch_size=1 \
    -o Train.warmup_steps=1000 -o Train.learning_rate=0.01 \
    -o Global.device=gpu:0,1,2,3,4,5,6,7 \
    -o Global.output='./output/instance_segmentation/SOLOv2_dy'