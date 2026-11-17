"""
mlp.py
====================================================
Multi-Layer Perceptron (MLP) with Backpropagation
(Generalized Delta Rule) เขียนจากศูนย์ ไม่ใช้ ML library
ใช้เฉพาะ Standard Library: random, math

CPE 261456 - Introduction to Computational Intelligence
Computer Assignment 1

โครงสร้างที่ปรับได้ (ไม่ต้องแก้โค้ด แค่เปลี่ยนตอนสร้าง object):
    - layer_sizes  : จำนวน hidden layer และจำนวน node ในแต่ละ layer
    - learning_rate: อัตราการเรียนรู้ (eta)
    - momentum     : อัตรา momentum (alpha)
    - seed         : สำหรับสุ่ม initial weight ให้ทำซ้ำได้
====================================================
"""

import random
import math


# ----------------------------------------------------------------
# Activation function: Sigmoid และอนุพันธ์ของมัน
# ----------------------------------------------------------------
def sigmoid(x):
    # ป้องกัน overflow กรณี x ติดลบมากๆ
    if x < -60:
        return 0.0
    if x > 60:
        return 1.0
    return 1.0 / (1.0 + math.exp(-x))


def sigmoid_derivative(y):
    # y คือ output ของ sigmoid ไปแล้ว (ไม่ใช่ x ดิบ)
    # อนุพันธ์ของ sigmoid เขียนในเทอมของ output ได้เป็น y*(1-y)
    return y * (1.0 - y)


class MLP:
    """
    Multi-Layer Perceptron พร้อม Backpropagation (Generalized Delta Rule)

    layer_sizes: list เช่น [8, 5, 3, 1]
        หมายถึง  8 input nodes -> hidden(5) -> hidden(3) -> 1 output node
        จะมีกี่ hidden layer กี่ node ก็ใส่เพิ่ม/ลดใน list นี้ได้เลย
    """

    def __init__(self, layer_sizes, learning_rate=0.1, momentum=0.9, seed=None):
        # ใช้ random generator ของแต่ละโมเดล เพื่อให้การสุ่มทำซ้ำได้
        # และไม่ไปรบกวนการสุ่มของส่วนแบ่งข้อมูลหรือโมเดลตัวอื่น
        self.rng = random.Random(seed)

        self.layer_sizes = layer_sizes
        self.num_layers = len(layer_sizes)  # รวม input layer ด้วย
        self.lr = learning_rate
        self.momentum = momentum



        # weights[l] = weight matrix เชื่อมระหว่าง layer l กับ layer l+1
        # weights[l][j][i] = น้ำหนักจาก node i (layer l) ไป node j (layer l+1)
        self.weights = []
        # biases[l] = bias ของแต่ละ node ใน layer l+1
        self.biases = []

        for l in range(self.num_layers - 1):
            n_in = layer_sizes[l]
            n_out = layer_sizes[l + 1]

            # สุ่ม initial weight ช่วงเล็กๆ รอบ 0 (มาตรฐานสำหรับ sigmoid)
            w = [[self.rng.uniform(-0.5, 0.5) for _ in range(n_in)] for _ in range(n_out)]
            b = [self.rng.uniform(-0.5, 0.5) for _ in range(n_out)]

            self.weights.append(w)
            self.biases.append(b)

        # เก็บค่า Δw, Δb ครั้งก่อนหน้า ไว้ใช้กับ momentum
        self.prev_dw = [[[0.0] * len(w[0]) for _ in w] for w in self.weights]
        self.prev_db = [[0.0] * len(b) for b in self.biases]

    # --------------------------------------------------------
    # FORWARD PASS
    # --------------------------------------------------------
    def forward(self, x):
        """
        x: list ของ input 1 ตัวอย่าง เช่น [0.5, 0.3, ...]
        คืนค่า: activations ของทุก layer (รวม input layer เป็น layer 0)
                activations[0] = input เดิม
                activations[-1] = output ของโครงข่าย
        """
        activations = [x]
        current = x

        for l in range(self.num_layers - 1):
            w = self.weights[l]
            b = self.biases[l]
            next_layer_output = []

            for j in range(len(w)):  # วนทุก node ใน layer ถัดไป
                net = b[j]
                for i in range(len(current)):
                    net += w[j][i] * current[i]
                next_layer_output.append(sigmoid(net))

            activations.append(next_layer_output)
            current = next_layer_output

        return activations

    # --------------------------------------------------------
    # BACKWARD PASS (1 training sample) + อัปเดต weight
    # --------------------------------------------------------
    def train_one_sample(self, x, target):
        activations = self.forward(x)
        output = activations[-1]

        # ---- 1) คำนวณ delta ของ output layer ----
        # delta_output = error * y*(1-y)
        deltas = [None] * (self.num_layers - 1)  # deltas[l] คือ delta ของ layer l+1
        output_delta = []
        for k in range(len(output)):
            error = target[k] - output[k]
            output_delta.append(error * sigmoid_derivative(output[k]))
        deltas[self.num_layers - 2] = output_delta

        # ---- 2) คำนวณ delta ของ hidden layer ทุกชั้น (ไล่จากหลังไปหน้า) ----
        for l in range(self.num_layers - 3, -1, -1):
            layer_output = activations[l + 1]
            next_delta = deltas[l + 1]
            next_weights = self.weights[l + 1]  # weight ที่เชื่อม layer นี้ -> layer ถัดไป

            layer_delta = []
            for j in range(len(layer_output)):
                # รวม delta จาก node ทุกตัวใน layer ถัดไป ที่เชื่อมกับ node j นี้
                error_sum = 0.0
                for k in range(len(next_delta)):
                    error_sum += next_delta[k] * next_weights[k][j]
                layer_delta.append(error_sum * sigmoid_derivative(layer_output[j]))

            deltas[l] = layer_delta

        # ---- 3) อัปเดต weight และ bias ทุกเส้น (พร้อม momentum) ----
        for l in range(self.num_layers - 1):
            layer_input = activations[l]       # output ของ layer ก่อนหน้า (=input ของเส้นนี้)
            layer_delta = deltas[l]
            w = self.weights[l]
            b = self.biases[l]

            for j in range(len(w)):            # node ปลายทาง
                for i in range(len(w[j])):      # node ต้นทาง
                    dw = self.lr * layer_delta[j] * layer_input[i] \
                         + self.momentum * self.prev_dw[l][j][i]
                    w[j][i] += dw
                    self.prev_dw[l][j][i] = dw

                db = self.lr * layer_delta[j] + self.momentum * self.prev_db[l][j]
                b[j] += db
                self.prev_db[l][j] = db

        # คืนค่า error (สำหรับใช้คำนวณ MSE ทั้ง epoch)
        return [target[k] - output[k] for k in range(len(output))]

    # --------------------------------------------------------
    # TRAIN หลาย epoch บนชุดข้อมูลทั้งหมด
    # --------------------------------------------------------
    def train(self, X, Y, epochs=1000, shuffle=True, verbose=True, print_every=100):
        n = len(X)
        history = []  # เก็บ MSE ของแต่ละ epoch ไว้ plot กราฟได้

        for ep in range(1, epochs + 1):
            indices = list(range(n))
            if shuffle:
                self.rng.shuffle(indices)

            sum_sq_error = 0.0
            for idx in indices:
                errors = self.train_one_sample(X[idx], Y[idx])
                for e in errors:
                    sum_sq_error += e * e

            mse = sum_sq_error / (n * len(Y[0]))
            history.append(mse)

            if verbose and (ep % print_every == 0 or ep == 1):
                print(f"Epoch {ep:5d}  MSE = {mse:.6f}")

        return history

    # --------------------------------------------------------
    # PREDICT (ไม่มีการอัปเดต weight)
    # --------------------------------------------------------
    def predict(self, x):
        return self.forward(x)[-1]


# ======================================================
# ทดสอบเบื้องต้นด้วยปัญหา XOR (แค่เช็คว่าโค้ดทำงานถูกต้อง)
# XOR เป็นปัญหาคลาสสิกที่ perceptron ชั้นเดียวแก้ไม่ได้
# แต่ MLP ที่มี hidden layer ต้องแก้ได้
# ======================================================
if __name__ == "__main__":
    X = [[0, 0], [0, 1], [1, 0], [1, 1]]
    Y = [[0], [1], [1], [0]]

    # 2 input -> 4 hidden -> 1 output
    net = MLP(layer_sizes=[2, 4, 1], learning_rate=0.5, momentum=0.8, seed=42)
    net.train(X, Y, epochs=5000, print_every=1000)

    print("\n--- ผลการทดสอบ XOR ---")
    for x, y in zip(X, Y):
        pred = net.predict(x)
        print(f"input={x}  target={y[0]}  predicted={pred[0]:.4f}")
