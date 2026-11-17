"""รันชุดการทดลอง MLP ตามค่าที่เปรียบเทียบ และบันทึก CSV ลง results/."""

import csv
import os

from run_cross import run_experiment as run_cross_experiment
from run_flood import run_experiment as run_flood_experiment


RESULTS_DIR = "results"
SPLIT_SEED = 42
FLOOD_EPOCHS = 300
CROSS_EPOCHS = 300
MSE_CHECKPOINTS = [1, 100, 200, 300]

# Baseline แล้วเปลี่ยนทีละปัจจัย เพื่อให้วิเคราะห์ผลได้ชัดเจน
FLOOD_CONFIGS = [
    ("F01-baseline", [5], 0.10, 0.50, 1),
    ("F02-hidden-3", [3], 0.10, 0.50, 1),
    ("F03-hidden-10", [10], 0.10, 0.50, 1),
    ("F04-two-hidden", [10, 5], 0.10, 0.50, 1),
    ("F05-lr-0.03", [5], 0.03, 0.50, 1),
    ("F06-lr-0.30", [5], 0.30, 0.50, 1),
    ("F07-momentum-0.0", [5], 0.10, 0.00, 1),
    ("F08-momentum-0.9", [5], 0.10, 0.90, 1),
    ("F09-weight-seed-42", [5], 0.10, 0.50, 42),
    ("F10-weight-seed-99", [5], 0.10, 0.50, 99),
]

CROSS_CONFIGS = [
    ("C01-baseline", [4], 0.10, 0.50, 1),
    ("C02-hidden-2", [2], 0.10, 0.50, 1),
    ("C03-hidden-8", [8], 0.10, 0.50, 1),
    ("C04-two-hidden", [8, 4], 0.10, 0.50, 1),
    ("C05-lr-0.03", [4], 0.03, 0.50, 1),
    ("C06-lr-0.30", [4], 0.30, 0.50, 1),
    ("C07-momentum-0.0", [4], 0.10, 0.00, 1),
    ("C08-momentum-0.9", [4], 0.10, 0.90, 1),
    ("C09-weight-seed-42", [4], 0.10, 0.50, 42),
    ("C10-weight-seed-99", [4], 0.10, 0.50, 99),
]


def layer_text(hidden_layers):
    return "-".join(str(node) for node in hidden_layers)


def save_csv(filename, fieldnames, rows):
    path = os.path.join(RESULTS_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


def run_flood_suite():
    summaries, folds = [], []
    print("=== Flood dataset: 10-fold cross validation ===")
    for run_id, hidden, learning_rate, momentum, weight_seed in FLOOD_CONFIGS:
        print(f"{run_id}: hidden={hidden}, lr={learning_rate}, momentum={momentum}, seed={weight_seed}")
        details = run_flood_experiment(
            hidden, learning_rate, momentum, epochs=FLOOD_EPOCHS,
            seed=weight_seed, split_seed=SPLIT_SEED, verbose=False,
            return_details=True, mse_checkpoints=MSE_CHECKPOINTS,
        )
        row = {
            "run_id": run_id, "hidden_layers": layer_text(hidden),
            "learning_rate": learning_rate, "momentum": momentum,
            "weight_seed": weight_seed, "split_seed": SPLIT_SEED,
            "epochs": FLOOD_EPOCHS, "average_mae": f"{details['average_mae']:.6f}",
            "std_mae": f"{details['std_mae']:.6f}",
        }
        for epoch, mse in details["mean_mse_at_epoch"].items():
            row[f"mean_mse_epoch_{epoch}"] = f"{mse:.6f}"
        summaries.append(row)
        for fold_number, mae in enumerate(details["fold_maes"], start=1):
            folds.append({**row, "fold": fold_number, "mae": f"{mae:.6f}"})
        print(f"  Average MAE = {details['average_mae']:.4f} ± {details['std_mae']:.4f}")

    save_csv("flood_summary.csv", list(summaries[0]), summaries)
    save_csv("flood_folds.csv", list(folds[0]), folds)


def run_cross_suite():
    summaries, folds = [], []
    print("\n=== cross.pat: 10-fold cross validation ===")
    for run_id, hidden, learning_rate, momentum, weight_seed in CROSS_CONFIGS:
        print(f"{run_id}: hidden={hidden}, lr={learning_rate}, momentum={momentum}, seed={weight_seed}")
        details = run_cross_experiment(
            hidden, learning_rate, momentum, epochs=CROSS_EPOCHS,
            seed=weight_seed, split_seed=SPLIT_SEED, verbose=False,
            return_details=True, mse_checkpoints=MSE_CHECKPOINTS,
        )
        matrix = details["confusion_matrix"]
        row = {
            "run_id": run_id, "hidden_layers": layer_text(hidden),
            "learning_rate": learning_rate, "momentum": momentum,
            "weight_seed": weight_seed, "split_seed": SPLIT_SEED,
            "epochs": CROSS_EPOCHS,
            "average_accuracy_percent": f"{details['average_accuracy'] * 100:.4f}",
            "std_accuracy_percent": f"{details['std_accuracy'] * 100:.4f}",
            "true0_pred0": matrix[0][0], "true0_pred1": matrix[0][1],
            "true1_pred0": matrix[1][0], "true1_pred1": matrix[1][1],
        }
        for epoch, mse in details["mean_mse_at_epoch"].items():
            row[f"mean_mse_epoch_{epoch}"] = f"{mse:.6f}"
        summaries.append(row)
        for fold_number, accuracy in enumerate(details["fold_accuracies"], start=1):
            folds.append({**row, "fold": fold_number,
                          "accuracy_percent": f"{accuracy * 100:.4f}"})
        print(f"  Average accuracy = {details['average_accuracy'] * 100:.2f}% ± {details['std_accuracy'] * 100:.2f}%")

    save_csv("cross_summary.csv", list(summaries[0]), summaries)
    save_csv("cross_folds.csv", list(folds[0]), folds)


if __name__ == "__main__":
    os.makedirs(RESULTS_DIR, exist_ok=True)
    run_flood_suite()
    run_cross_suite()
    print("\nบันทึกผลแล้วใน results/")
