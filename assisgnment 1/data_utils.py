"""
data_utils.py
====================================================
ฟังก์ชันช่วยเหลือสำหรับ:
  1. อ่านไฟล์ Flood_dataset.txt และ cross.pat
  2. Normalize / Denormalize ข้อมูล (min-max scaling)
  3. แบ่งข้อมูลแบบ k-fold cross validation (ใช้กับ 10% CV)
  4. คำนวณ Confusion Matrix และ Accuracy

ไม่ใช้ library ภายนอกใดๆ ใช้แค่ standard library
====================================================
"""

import random


# ==================================================
# 1) โหลดข้อมูล
# ==================================================
def load_flood_dataset(path):
    """
    อ่านไฟล์ Flood_dataset.txt (มี 2 บรรทัด header ให้ข้าม)
    คืนค่า X (list ของ list, 8 inputs ต่อแถว), Y (list ของ list, 1 output ต่อแถว)
    """
    X, Y = [], []
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines[2:]:  # ข้าม 2 บรรทัด header
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        values = [float(v) for v in parts]
        X.append(values[:8])   # 8 inputs แรก
        Y.append([values[8]])  # output ตัวสุดท้าย

    return X, Y


def load_cross_pat(path):
    """
    อ่านไฟล์ cross.pat รูปแบบ:
        p0
        0.0902  0.2690
        1 0
        p1
        ...
    คืนค่า X (2 features ต่อแถว), Y (one-hot 2 classes ต่อแถว)
    """
    X, Y = [], []
    with open(path, "r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f.readlines() if ln.strip() != ""]

    # วนทีละ 3 บรรทัด: ชื่อ pattern, features, class
    for i in range(0, len(lines), 3):
        # lines[i]   -> ชื่อ pattern เช่น "p0" (ไม่ใช้)
        feature_line = lines[i + 1]
        class_line = lines[i + 2]

        features = [float(v) for v in feature_line.split()]
        classes = [float(v) for v in class_line.split()]

        X.append(features)
        Y.append(classes)

    return X, Y


# ==================================================
# 2) Normalize / Denormalize (min-max scaling)
#    ใช้ช่วง [0.1, 0.9] แทน [0,1] เพราะ sigmoid จริงๆ
#    แล้วไม่มีวันแตะ 0 หรือ 1 พอดี (ช่วยให้ train ง่ายขึ้น)
# ==================================================
def compute_min_max(data):
    """data: list ของ list (หลายคอลัมน์) -> คืนค่า min, max ต่อคอลัมน์"""
    n_cols = len(data[0])
    mins = [min(row[c] for row in data) for c in range(n_cols)]
    maxs = [max(row[c] for row in data) for c in range(n_cols)]
    return mins, maxs


def normalize(data, mins, maxs, low=0.1, high=0.9):
    result = []
    for row in data:
        new_row = []
        for c, v in enumerate(row):
            if maxs[c] == mins[c]:      # กันหารด้วย 0 กรณีคอลัมน์ค่าคงที่
                new_row.append(low)
            else:
                scaled = (v - mins[c]) / (maxs[c] - mins[c])
                new_row.append(scaled * (high - low) + low)
        result.append(new_row)
    return result


def denormalize_value(v, col_min, col_max, low=0.1, high=0.9):
    """แปลงค่ากลับจาก [low, high] ไปเป็นสเกลจริง (ใช้ตอนดู output ของ flood)"""
    return (v - low) / (high - low) * (col_max - col_min) + col_min


# ==================================================
# 3) K-Fold Cross Validation split
# ==================================================
def make_k_folds(n_samples, k=10, seed=42):
    """
    คืนค่า list ของ fold แต่ละ fold คือ list ของ index
    ใช้กับ 10% cross validation (k=10 -> เทส 10%, เทรน 90% ต่อรอบ)
    """
    indices = list(range(n_samples))
    random.seed(seed)
    random.shuffle(indices)

    folds = [[] for _ in range(k)]
    for idx, sample_i in enumerate(indices):
        folds[idx % k].append(sample_i)
    return folds


def get_train_test_split(X, Y, folds, test_fold_index):
    """เอา fold ที่ test_fold_index เป็น test set ที่เหลือเป็น train set"""
    test_idx = set(folds[test_fold_index])
    X_train, Y_train, X_test, Y_test = [], [], [], []

    for i in range(len(X)):
        if i in test_idx:
            X_test.append(X[i])
            Y_test.append(Y[i])
        else:
            X_train.append(X[i])
            Y_train.append(Y[i])

    return X_train, Y_train, X_test, Y_test


# ==================================================
# 4) Confusion Matrix / Accuracy (สำหรับ cross.pat - classification)
# ==================================================
def confusion_matrix(y_true, y_pred, n_classes=2):
    """
    y_true, y_pred: list ของ one-hot vector เช่น [1,0] หรือ [0,1]
    คืนค่า confusion matrix ขนาด n_classes x n_classes
    matrix[actual][predicted]
    """
    matrix = [[0] * n_classes for _ in range(n_classes)]
    for true_vec, pred_vec in zip(y_true, y_pred):
        actual_class = true_vec.index(max(true_vec))
        predicted_class = pred_vec.index(max(pred_vec))
        matrix[actual_class][predicted_class] += 1
    return matrix


def print_confusion_matrix(matrix):
    n = len(matrix)
    header = "        " + "".join(f"Pred{j:<6}" for j in range(n))
    print(header)
    for i, row in enumerate(matrix):
        row_str = "".join(f"{v:<10}" for v in row)
        print(f"True{i:<4}{row_str}")


def accuracy_from_confusion(matrix):
    total = sum(sum(row) for row in matrix)
    correct = sum(matrix[i][i] for i in range(len(matrix)))
    return correct / total if total > 0 else 0.0


def mean_absolute_error(y_true, y_pred):
    """สำหรับ flood dataset (regression) - ใช้วัดผลแทน accuracy"""
    total = 0.0
    count = 0
    for t, p in zip(y_true, y_pred):
        for tv, pv in zip(t, p):
            total += abs(tv - pv)
            count += 1
    return total / count if count > 0 else 0.0


def mean_and_sample_std(values):
    """คืนค่าเฉลี่ยและ sample standard deviation โดยคำนวณเอง"""
    if not values:
        return 0.0, 0.0
    mean = sum(values) / len(values)
    if len(values) == 1:
        return mean, 0.0
    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
    return mean, variance ** 0.5
