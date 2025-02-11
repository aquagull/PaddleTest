python main.py -c paddlex/configs/modules/ts_anomaly_detection/TimesNet_ad.yaml -o Global.mode=train -o Train.feature_cols="feature_0,feature_1,feature_2,feature_3,feature_4,feature_5,feature_6,feature_7,feature_8,feature_9,feature_10,feature_11,feature_12,feature_13,feature_14,feature_15,feature_16,feature_17,feature_18,feature_19,feature_20,feature_21,feature_22,feature_23,feature_24" -o Global.dataset_dir="../PSM" -o Train.input_len=100 -o Train.batch_size=128  -o Train.learning_rate=0.0005 -o Train.epochs_iters=3 -o Global.output='./output/ts_anomaly_detection/TimesNet_ad_dy'

python main.py -c paddlex/configs/modules/ts_anomaly_detection/TimesNet_ad.yaml -o Global.mode=evaluate -o Global.dataset_dir="../PSM" -o Evaluate.weight_path='./output/ts_forecast/TimesNet_ad_dy/best_accuracy.pdparams.tar' -o Global.output='./output/ts_anomaly_detection/TimesNet_ad_dy_eval'
