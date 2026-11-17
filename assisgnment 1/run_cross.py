"""
run_cross.py
====================================================
ทดลอง Classification บน cross.pat (2 classes, 2 features)
ทำ 10% cross validation (10-fold) พร้อมแสดง Confusion Matrix
====================================================
"""

from mlp import MLP
from data_utils import (
    load_cross_pat, make_k_folds, get_train_test_split,
    confusion_matrix, print_confusion_matrix, accuracy_from_confusion,
    mean_and_sample_std
)


def run_experiment(hidden_layers, learning_rate, momentum, epochs=500, seed=1,
                   verbose=True, return_details=False, split_seed=None,
                   mse_checkpoints=None):
    """
    hidden_layers: list เช่น [4] หรือ [8, 4]
    คืนค่า: overall confusion matrix (รวมทุก fold) และ accuracy เฉลี่ย
    """
    X, Y = load_cross_pat("data/cross.pat")
    # cross.pat ค่าอยู่ในช่วง 0-1 อยู่แล้ว (จากลักษณะข้อมูล) ไม่ต้อง normalize เพิ่ม

    # แยก seed ของการแบ่ง fold ออกจาก seed ของ initial weights
    if split_seed is None:
        split_seed = seed
    folds = make_k_folds(len(X), k=10, seed=split_seed)
    layer_sizes = [2] + hidden_layers + [2]

    overall_matrix = [[0, 0], [0, 0]]
    fold_accuracies = []
    checkpoint_values = {epoch: [] for epoch in (mse_checkpoints or []) if epoch <= epochs}

    for fold_i in range(10):
        X_train, Y_train, X_test, Y_test = get_train_test_split(X, Y, folds, fold_i)

        net = MLP(layer_sizes, learning_rate=learning_rate,
                  momentum=momentum, seed=seed + fold_i)
        history = net.train(X_train, Y_train, epochs=epochs, verbose=False)
        for epoch in checkpoint_values:
            checkpoint_values[epoch].append(history[epoch - 1])

        Y_pred = [net.predict(x) for x in X_test]

        fold_matrix = confusion_matrix(Y_test, Y_pred, n_classes=2)
        acc = accuracy_from_confusion(fold_matrix)
        fold_accuracies.append(acc)

        # รวมเข้า overall matrix
        for i in range(2):
            for j in range(2):
                overall_matrix[i][j] += fold_matrix[i][j]

        if verbose:
            print(f"  Fold {fold_i+1:2d}/10  Accuracy = {acc*100:.2f}%")

    avg_acc = sum(fold_accuracies) / len(fold_accuracies)
    if return_details:
        _, std_acc = mean_and_sample_std(fold_accuracies)
        return {
            "average_accuracy": avg_acc,
            "std_accuracy": std_acc,
            "fold_accuracies": fold_accuracies,
            "confusion_matrix": overall_matrix,
            "mean_mse_at_epoch": {
                epoch: sum(values) / len(values) for epoch, values in checkpoint_values.items()
            },
        }
    return overall_matrix, avg_acc


if __name__ == "__main__":
    print("=== ทดลองที่ 1: hidden=[4], lr=0.3, momentum=0.6 ===")
    matrix, avg_acc = run_experiment(hidden_layers=[4], learning_rate=0.3,
                                      momentum=0.6, epochs=300)
    print(f"\nAverage Accuracy (10-fold) = {avg_acc*100:.2f}%")
    print("Overall Confusion Matrix (รวมทุก fold):")
    print_confusion_matrix(matrix)

    print("\n=== ทดลองที่ 2: hidden=[8, 4] (2 hidden layers), lr=0.5, momentum=0.8 ===")
    matrix, avg_acc = run_experiment(hidden_layers=[8, 4], learning_rate=0.5,
                                      momentum=0.8, epochs=300)
    print(f"\nAverage Accuracy (10-fold) = {avg_acc*100:.2f}%")
    print("Overall Confusion Matrix (รวมทุก fold):")
    print_confusion_matrix(matrix)
