#dataset_dir="/Users/vionwinnie/Projects/photo-studio/u2net_saved_models"
#score_dir="/Users/vionwinnie/Projects/photo-studio/eval_metrics"
dataset_dir="./datasets"
score_dir="."

python main.py \
 --pred_root_dir ${dataset_dir} \
 --save_dir ${score_dir} \
 --methods "Method_1 Method_2"\
 --datasets "Dataset_1 Dataset_2" \
 --cuda False

