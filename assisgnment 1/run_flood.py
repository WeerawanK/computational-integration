"""
run_flood.py
====================================================
ทดลอง Predict ระดับน้ำที่สะพานนวรัตน์ (t+7) ด้วย MLP
ใช้ Flood_dataset.txt (8 inputs -> 1 output)
ทำ 10% cross validation (10-fold)
====================================================
"""

from mlp import MLP
from data_utils import (
    load_flood_dataset, compute_min_max, normalize, denormalize_value,
    make_k_folds, get_train_test_split, mean_absolute_error, mean_and_sample_std
)


def run_experiment(hidden_layers, learning_rate, momentum, epochs=500, seed=1,
                   verbose=True, return_details=False, split_seed=None,
                   mse_checkpoints=None):
    """
    hidden_layers: list เช่น [8] หรือ [10, 5] (จำนวน node ใน hidden layer แต่ละชั้น)
    คืนค่า: ค่าเฉลี่ย MAE (บนสเกลจริง หน่วยเดียวกับระดับน้ำ) จากทั้ง 10 fold
    """
    X, Y = load_flood_dataset("data/Flood_dataset.txt")

    # ใช้ split_seed แยกจาก seed ของน้ำหนัก เพื่อเปรียบเทียบ initial weight
    # โดยยังใช้ชุด train/test เดิมได้
    if split_seed is None:
        split_seed = seed
    folds = make_k_folds(len(X), k=10, seed=split_seed)

    layer_sizes = [8] + hidden_layers + [1]
    fold_maes = []
    checkpoint_values = {epoch: [] for epoch in (mse_checkpoints or []) if epoch <= epochs}

    for fold_i in range(10):
        # แบ่งข้อมูลดิบก่อน แล้วหา min/max จาก training set เท่านั้น
        # เพื่อไม่ให้ข้อมูลใน test set รั่วเข้าไปมีผลต่อการ normalize
        X_train_raw, Y_train_raw, X_test_raw, Y_test_raw = get_train_test_split(
            X, Y, folds, fold_i
        )
        x_mins, x_maxs = compute_min_max(X_train_raw)
        y_mins, y_maxs = compute_min_max(Y_train_raw)
        X_train = normalize(X_train_raw, x_mins, x_maxs)
        Y_train = normalize(Y_train_raw, y_mins, y_maxs)
        X_test = normalize(X_test_raw, x_mins, x_maxs)

        net = MLP(layer_sizes, learning_rate=learning_rate,
                  momentum=momentum, seed=seed + fold_i)
        history = net.train(X_train, Y_train, epochs=epochs, verbose=False)
        for epoch in checkpoint_values:
            checkpoint_values[epoch].append(history[epoch - 1])

        # predict บน test set แล้วแปลงกลับเป็นสเกลจริงก่อนวัด error
        y_true_real, y_pred_real = [], []
        for x, y_true_real_value in zip(X_test, Y_test_raw):
            y_pred_norm = net.predict(x)
            y_pred_real.append([denormalize_value(y_pred_norm[0], y_mins[0], y_maxs[0])])
            y_true_real.append(y_true_real_value)

        mae = mean_absolute_error(y_true_real, y_pred_real)
        fold_maes.append(mae)
        if verbose:
            print(f"  Fold {fold_i+1:2d}/10  MAE = {mae:.3f}")

    avg_mae = sum(fold_maes) / len(fold_maes)
    if return_details:
        _, std_mae = mean_and_sample_std(fold_maes)
        return {
            "average_mae": avg_mae,
            "std_mae": std_mae,
            "fold_maes": fold_maes,
            "mean_mse_at_epoch": {
                epoch: sum(values) / len(values) for epoch, values in checkpoint_values.items()
            },
        }
    return avg_mae


if __name__ == "__main__":
    print("=== ทดลองที่ 1: hidden=[5], lr=0.1, momentum=0.9 ===")
    avg = run_experiment(hidden_layers=[5], learning_rate=0.1, momentum=0.9, epochs=300)
    print(f"ค่าเฉลี่ย MAE ทั้ง 10 fold = {avg:.3f}\n")

    print("=== ทดลองที่ 2: hidden=[10], lr=0.3, momentum=0.5 ===")
    avg = run_experiment(hidden_layers=[10], learning_rate=0.3, momentum=0.5, epochs=300)
    print(f"ค่าเฉลี่ย MAE ทั้ง 10 fold = {avg:.3f}\n")

    # ตัวอย่าง: ลองเปลี่ยนจำนวน hidden layer เป็น 2 ชั้น
    print("=== ทดลองที่ 3: hidden=[10, 5] (2 hidden layers), lr=0.2, momentum=0.7 ===")
    avg = run_experiment(hidden_layers=[10, 5], learning_rate=0.2, momentum=0.7, epochs=300)
    print(f"ค่าเฉลี่ย MAE ทั้ง 10 fold = {avg:.3f}\n")
