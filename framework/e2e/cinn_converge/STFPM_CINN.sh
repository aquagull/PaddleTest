python main.py -c paddlex/configs/modules/image_anomaly_detection/STFPM.yaml -o Global.mode=train -o Global.dataset_dir=../mvtec_grid -o Train.epochs_iters=1000 -o Global.output='./output/image_anomaly_detection/STFPM_CINN' -o Train.dy2st=True