python main.py -c paddlex/configs/modules/text_detection/PP-OCRv3_server_det.yaml -o Global.dataset_dir=../icdar2015 -o Global.mode=train -o Train.learning_rate=0.0005 -o Train.epochs_iters=50 -o Global.output='./output/text_detection/PP-OCRv3_server_det_CINN' -o Train.dy2st=True