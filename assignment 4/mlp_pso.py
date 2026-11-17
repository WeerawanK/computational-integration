"""
Train Multilayer Perceptron ด้วย Particle Swarm Optimization (PSO)
สำหรับพยากรณ์ค่า Benzene ล่วงหน้า 5 วันและ 10 วัน

โปรแกรมนี้เขียนขึ้นสำหรับ Assignment 4
ใช้ numpy เฉพาะการคำนวณตัวเลขและเมทริกซ์เท่านั้น
ไม่ได้ใช้ไลบรารีสำเร็จรูปสำหรับ Machine Learning หรือการฝึก Neural Network
"""

import csv
import math
import random
import statistics
import time
import zipfile
from pathlib import Path
from xml.etree import ElementTree

import numpy as np


# ไฟล์ทั้งหมดอยู่โฟลเดอร์เดียวกับโปรแกรม ทำให้ย้ายโฟลเดอร์ได้ง่าย
FOLDER = Path(__file__).parent
DATA_FILE = FOLDER / "AirQualityUCI.xlsx"
RESULT_FILE = FOLDER / "results.csv"
SUMMARY_FILE = FOLDER / "summary.csv"

# attribute ที่ใช้เป็น input ตามโจทย์
INPUT_COLUMNS = [3, 6, 8, 10, 11, 12, 13, 14]

# attribute ที่ต้องการพยากรณ์ คือ Benzene หมายเลข 5
TARGET_COLUMN = 5

# ค่าพิเศษ -200 ในชุดข้อมูลหมายถึงข้อมูลหาย ไม่ใช่ค่าจริง
MISSING_VALUE = -200.0

# ทดลองเปลี่ยนจำนวน hidden layer และ nodes ตามโจทย์
NETWORKS = {
    "8": [8],
    "16": [16],
    "8-8": [8, 8],
    "12-6": [12, 6],
}

# ค่าหลักของ PSO ใช้ค่าคงที่เพื่อให้ทดลองซ้ำได้
PARTICLE_COUNT = 12
ITERATIONS = 15
INERTIA = 0.70
COGNITIVE = 1.40
SOCIAL = 1.40
FOLDS = 10


def excel_column_number(cell_reference):
    """แปลงชื่อคอลัมน์ Excel เช่น A หรือ AA เป็นหมายเลขเริ่มจาก 0"""
    letters = ""
    for character in cell_reference:
        if character.isalpha():
            letters += character.upper()
        else:
            break

    number = 0
    for character in letters:
        number = number * 26 + ord(character) - ord("A") + 1
    return number - 1


def read_air_quality_xlsx(filename):
    """อ่านข้อมูลจากไฟล์ xlsx โดยใช้ zipfile และ XML ของ Python

    xlsx เป็นไฟล์ zip ที่เก็บข้อมูลตารางไว้ใน XML
    วิธีนี้ทำให้โปรแกรมอ่านไฟล์ข้อมูลได้โดยไม่ต้องใช้ pandas หรือ openpyxl
    """
    namespace = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

    with zipfile.ZipFile(filename, "r") as workbook:
        shared_text = []
        shared_root = ElementTree.fromstring(workbook.read("xl/sharedStrings.xml"))

        # ข้อความใน Excel บางส่วนเก็บไว้ใน sharedStrings.xml แล้วอ้างด้วย index
        for item in shared_root.findall("x:si", namespace):
            shared_text.append("".join(item.itertext()))

        sheet_root = ElementTree.fromstring(
            workbook.read("xl/worksheets/sheet1.xml")
        )

    all_rows = []
    row_elements = sheet_root.findall(".//x:sheetData/x:row", namespace)

    for row_element in row_elements[1:]:
        # สร้างแถวที่มี 15 ช่อง ตาม attribute 0 ถึง 14
        row = [None] * 15

        for cell in row_element.findall("x:c", namespace):
            reference = cell.get("r", "A1")
            column = excel_column_number(reference)
            if column >= len(row):
                continue

            value_element = cell.find("x:v", namespace)
            if value_element is None:
                continue

            value = value_element.text
            if cell.get("t") == "s":
                value = shared_text[int(value)]

            try:
                row[column] = float(value)
            except (TypeError, ValueError):
                # Date และ Time ไม่ได้ใช้เป็น input โดยตรง จึงเก็บเป็น None
                row[column] = None

        # แถวที่ไม่มีข้อมูลตัวเลขเลยไม่นับเป็นข้อมูลจริง
        if any(value is not None for value in row[2:]):
            all_rows.append(row)

    return all_rows


def make_supervised_rows(rows, hours_ahead):
    """สร้าง input และ target สำหรับการพยากรณ์ล่วงหน้า

    ข้อมูลเป็นรายชั่วโมง ดังนั้น 5 วัน = 120 ชั่วโมง และ 10 วัน = 240 ชั่วโมง
    target ของแถวปัจจุบันคือ Benzene ที่อยู่ห่างออกไปตาม hours_ahead
    """
    inputs = []
    targets = []

    for current_index in range(len(rows) - hours_ahead):
        future_index = current_index + hours_ahead
        input_row = rows[current_index]
        target_row = rows[future_index]

        input_values = [input_row[column] for column in INPUT_COLUMNS]
        target_value = target_row[TARGET_COLUMN]

        # ตัดแถวที่มี missing value ออก เพื่อไม่ให้ -200 ทำให้ผลทดลองผิด
        if target_value is None or target_value == MISSING_VALUE:
            continue
        if any(value is None or value == MISSING_VALUE for value in input_values):
            continue

        inputs.append(input_values)
        targets.append(target_value)

    return np.asarray(inputs, dtype=float), np.asarray(targets, dtype=float)


def make_folds(number_of_rows, seed):
    """สุ่ม index แล้วแบ่งเป็น 10 folds

    งานนี้เป็น regression จึงไม่สามารถแบ่งตาม class แบบ Assignment 3 ได้
    แต่ใช้ seed เดิมเพื่อให้การแบ่งข้อมูลทำซ้ำได้
    """
    indices = list(range(number_of_rows))
    random_generator = random.Random(seed)
    random_generator.shuffle(indices)

    folds = [[] for _ in range(FOLDS)]
    for position, index in enumerate(indices):
        folds[position % FOLDS].append(index)
    return folds


def scale_data(train_x, test_x, train_y, test_y):
    """ปรับข้อมูลด้วยค่าเฉลี่ยและส่วนเบี่ยงเบนมาตรฐานของ train เท่านั้น

    การใช้ค่า train เท่านั้นช่วยป้องกันข้อมูลจาก test รั่วเข้าไปตอนฝึก
    """
    x_mean = train_x.mean(axis=0)
    x_std = train_x.std(axis=0)
    y_mean = train_y.mean()
    y_std = train_y.std()

    # ถ้าคอลัมน์ใดมีค่าเท่ากันหมด ให้ใช้ 1 แทนการหารด้วยศูนย์
    x_std[x_std == 0] = 1.0
    if y_std == 0:
        y_std = 1.0

    scaled_train_x = (train_x - x_mean) / x_std
    scaled_test_x = (test_x - x_mean) / x_std
    scaled_train_y = (train_y - y_mean) / y_std
    scaled_test_y = (test_y - y_mean) / y_std

    information = (x_mean, x_std, y_mean, y_std)
    return scaled_train_x, scaled_test_x, scaled_train_y, scaled_test_y, information


def sigmoid(values):
    """ฟังก์ชัน sigmoid ใช้ใน hidden layer ของ MLP"""
    values = np.clip(values, -40, 40)
    return 1.0 / (1.0 + np.exp(-values))


def count_weights(network):
    """นับจำนวน weight และ bias ทั้งหมดใน network"""
    layers = [len(INPUT_COLUMNS)] + network + [1]
    total = 0
    for before, after in zip(layers[:-1], layers[1:]):
        total += (before + 1) * after
    return total


def chromosome_to_matrices(position, network):
    """แปลง vector ของ PSO เป็น matrix weight ของแต่ละ layer"""
    layers = [len(INPUT_COLUMNS)] + network + [1]
    matrices = []
    start = 0

    for before, after in zip(layers[:-1], layers[1:]):
        width = before + 1
        size = width * after
        matrix = position[start:start + size].reshape(after, width)
        matrices.append(matrix)
        start += size

    return matrices


def forward(position, network, inputs):
    """คำนวณ output ของ MLP จาก input หลายแถวพร้อมกัน"""
    values = inputs
    matrices = chromosome_to_matrices(position, network)

    for layer_number, matrix in enumerate(matrices):
        # เติมคอลัมน์ 1 เพื่อให้ bias อยู่ใน matrix เดียวกับ weight
        with_bias = np.concatenate(
            [values, np.ones((values.shape[0], 1))], axis=1
        )
        values = with_bias @ matrix.T

        # output layer ใช้ค่าตรง ๆ เพราะเป็น regression
        if layer_number != len(matrices) - 1:
            values = sigmoid(values)

    return values[:, 0]


def mean_squared_error(position, network, inputs, targets):
    """ค่า fitness ภายใน PSO ใช้ MSE เพราะเหมาะกับการ optimize ต่อเนื่อง"""
    predictions = forward(position, network, inputs)
    errors = predictions - targets
    return float(np.mean(errors * errors))


def train_with_pso(train_x, train_y, network, seed):
    """ฝึกน้ำหนัก MLP ด้วย Particle Swarm Optimization"""
    random_generator = np.random.default_rng(seed)
    number_of_weights = count_weights(network)

    # ตำแหน่งเริ่มต้นคือน้ำหนักของแต่ละ particle
    positions = random_generator.uniform(
        -1.0, 1.0, size=(PARTICLE_COUNT, number_of_weights)
    )
    velocities = np.zeros_like(positions)

    personal_best_positions = positions.copy()
    personal_best_scores = np.full(PARTICLE_COUNT, np.inf)
    global_best_position = positions[0].copy()
    global_best_score = math.inf

    for _ in range(ITERATIONS):
        # คำนวณ fitness ของทุก particle แล้วจำตำแหน่งที่ดีที่สุด
        for particle in range(PARTICLE_COUNT):
            score = mean_squared_error(
                positions[particle], network, train_x, train_y
            )

            if score < personal_best_scores[particle]:
                personal_best_scores[particle] = score
                personal_best_positions[particle] = positions[particle].copy()

            if score < global_best_score:
                global_best_score = score
                global_best_position = positions[particle].copy()

        # ปรับความเร็วและตำแหน่งของ particle ตามสูตร PSO
        for particle in range(PARTICLE_COUNT):
            random_a = random_generator.random(number_of_weights)
            random_b = random_generator.random(number_of_weights)

            velocities[particle] = (
                INERTIA * velocities[particle]
                + COGNITIVE * random_a
                * (personal_best_positions[particle] - positions[particle])
                + SOCIAL * random_b
                * (global_best_position - positions[particle])
            )
            positions[particle] += velocities[particle]
            positions[particle] = np.clip(positions[particle], -5.0, 5.0)

    return global_best_position, global_best_score


def calculate_mae(actual, predicted):
    """คำนวณ Mean Absolute Error ในหน่วย Benzene เดิม"""
    return float(np.mean(np.abs(actual - predicted)))


def evaluate_configuration(inputs, targets, network_name, network, horizon_name):
    """ทำ 10-fold cross-validation ให้หนึ่ง configuration"""
    folds = make_folds(len(inputs), seed=2026)
    records = []

    for fold_number in range(FOLDS):
        test_indices = np.asarray(folds[fold_number], dtype=int)
        train_indices = np.asarray(
            [index for number, fold in enumerate(folds) if number != fold_number for index in fold],
            dtype=int,
        )

        train_x = inputs[train_indices]
        test_x = inputs[test_indices]
        train_y = targets[train_indices]
        test_y = targets[test_indices]

        train_x, test_x, train_y_scaled, test_y_scaled, scale = scale_data(
            train_x, test_x, train_y, test_y
        )
        _, _, train_y_mean, train_y_std = scale

        start_time = time.time()
        seed = 4000 + (fold_number + 1) * 100 + len(network) * 10
        best_position, best_mse = train_with_pso(
            train_x, train_y_scaled, network, seed
        )

        # แปลง prediction กลับเป็นหน่วย Benzene เดิมก่อนหา MAE
        train_prediction_scaled = forward(best_position, network, train_x)
        test_prediction_scaled = forward(best_position, network, test_x)
        train_prediction = train_prediction_scaled * train_y_std + train_y_mean
        test_prediction = test_prediction_scaled * train_y_std + train_y_mean

        seconds = time.time() - start_time
        records.append(
            {
                "horizon": horizon_name,
                "configuration": network_name,
                "hidden_layers": "-".join(str(value) for value in network),
                "fold": fold_number + 1,
                "train_mae": calculate_mae(targets[train_indices], train_prediction),
                "test_mae": calculate_mae(targets[test_indices], test_prediction),
                "best_mse_scaled": best_mse,
                "seconds": seconds,
            }
        )

        print(
            horizon_name,
            network_name,
            "fold",
            fold_number + 1,
            "test MAE =",
            round(records[-1]["test_mae"], 4),
        )

    return records


def summarize(records):
    """สรุปค่าเฉลี่ยและ SD ของ MAE จาก 10 folds"""
    grouped = {}
    for record in records:
        key = (record["horizon"], record["configuration"])
        grouped.setdefault(key, []).append(record)

    summaries = []
    for (horizon, configuration), selected in grouped.items():
        test_values = [row["test_mae"] for row in selected]
        train_values = [row["train_mae"] for row in selected]
        summaries.append(
            {
                "horizon": horizon,
                "configuration": configuration,
                "hidden_layers": selected[0]["hidden_layers"],
                "folds": len(selected),
                "train_mae_mean": statistics.mean(train_values),
                "test_mae_mean": statistics.mean(test_values),
                "test_mae_stdev": statistics.stdev(test_values),
                "seconds_mean": statistics.mean(row["seconds"] for row in selected),
            }
        )
    return summaries


def save_csv(records, summaries):
    """บันทึกผลละเอียดและผลสรุปเพื่อใช้ทำตารางในรายงาน"""
    record_fields = [
        "horizon", "configuration", "hidden_layers", "fold",
        "train_mae", "test_mae", "best_mse_scaled", "seconds",
    ]
    with open(RESULT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=record_fields)
        writer.writeheader()
        writer.writerows(records)

    summary_fields = [
        "horizon", "configuration", "hidden_layers", "folds",
        "train_mae_mean", "test_mae_mean", "test_mae_stdev", "seconds_mean",
    ]
    with open(SUMMARY_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=summary_fields)
        writer.writeheader()
        writer.writerows(summaries)


def main():
    """ลำดับหลักของการทดลองทั้งหมด"""
    print("กำลังอ่าน AirQualityUCI.xlsx")
    rows = read_air_quality_xlsx(DATA_FILE)
    print("จำนวนแถวที่อ่านได้ =", len(rows))

    all_records = []
    horizons = [("5_days", 120), ("10_days", 240)]

    for horizon_name, hours_ahead in horizons:
        inputs, targets = make_supervised_rows(rows, hours_ahead)
        print(horizon_name, "จำนวนตัวอย่างที่ใช้ =", len(inputs))

        for network_name, network in NETWORKS.items():
            all_records.extend(
                evaluate_configuration(
                    inputs, targets, network_name, network, horizon_name
                )
            )

    summaries = summarize(all_records)
    save_csv(all_records, summaries)

    print("บันทึกผลแล้ว:", RESULT_FILE)
    print("บันทึกผลสรุปแล้ว:", SUMMARY_FILE)


if __name__ == "__main__":
    main()
