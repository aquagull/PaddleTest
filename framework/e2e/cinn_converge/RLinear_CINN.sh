python main.py -c paddlex/configs/modules/ts_forecast/RLinear.yaml -o Global.mode=train -o Global.dataset_dir=../Etth1/Etth1_train -o Train.target_cols="HUFL,HULL,MUFL,MULL,LUFL,LULL,OT" -o Train.batch_size=32 -o Train.learning_rate=0.005 -o Train.patience=3 -o Train.epochs_iters=10 -o Global.output='./output/ts_forecast/RLinear_CINN' -o Train.dy2st=True

python main.py -c paddlex/configs/modules/ts_forecast/RLinear.yaml -o Global.mode=evaluate -o Global.dataset_dir=../Etth1/Etth1_val -o Evaluate.weight_path='./output/ts_forecast/RLinear_CINN/best_accuracy.pdparams.tar' -o Global.output='./output/ts_forecast/RLinear_CINN_eval' -o Train.dy2st=True
