"""โปรแกรมฝึก MLP ด้วย Genetic Algorithm
"""

import csv                 # ใช้อ่านไฟล์ข้อมูลที่คั่นด้วย comma
import math                # ใช้ exp ใน sigmoid และคำนวณค่า error
import random              # ใช้สุ่มข้อมูล น้ำหนัก และการกลายพันธุ์
import statistics          # ใช้หาค่าเฉลี่ยและส่วนเบี่ยงเบนมาตรฐาน
import time                # ใช้วัดเวลาที่ใช้ฝึกแต่ละ fold
from pathlib import Path   # ใช้จัดการชื่อไฟล์ให้ทำงานได้ทุกโฟลเดอร์

# -----------------------------------------------------------------------------
# กำหนดชื่อไฟล์ที่ใช้ในงาน
# -----------------------------------------------------------------------------
# Path(__file__) คือที่อยู่ของไฟล์ Python นี้
# การใช้วิธีนี้ทำให้โปรแกรมหาไฟล์ wdbc.data ที่อยู่โฟลเดอร์เดียวกันได้เสมอ
FOLDER = Path(__file__).parent
DATA_FILE = FOLDER / "wdbc.data"
RESULT_FILE = FOLDER / "results.csv"


# -----------------------------------------------------------------------------
# ส่วนที่ 1: อ่านและเตรียมข้อมูล
# -----------------------------------------------------------------------------
def read_data(filename):
    """อ่านข้อมูล WDBC แล้วคืนค่าเป็น list ของข้อมูลแต่ละแถว

    ในไฟล์ wdbc.data แต่ละแถวมีข้อมูล 32 ค่า ได้แก่
    ค่าแรก       = ID ของ sample
    ค่าที่สอง    = diagnosis โดย B คือ benign และ M คือ malignant
    ค่าที่เหลือ  = feature จำนวน 30 ค่า

    ID ไม่ถูกนำไปใช้เป็น input เพราะ ID ไม่ใช่คุณสมบัติของก้อนเนื้อ
    ส่วน diagnosis จะเปลี่ยนเป็นตัวเลขเพื่อให้เครือข่ายนำไปคำนวณได้
    B = 0 และ M = 1
    """
    # data จะเก็บข้อมูลทุกแถวในรูปแบบ list ของ dictionary
    # dictionary ทำให้เวลาเรียกใช้เราอ่านได้ง่าย เช่น sample["features"]
    data = []

    # เปิดไฟล์แบบอ่านอย่างเดียว โดยกำหนด encoding เป็น utf-8
    # with ช่วยปิดไฟล์ให้อัตโนมัติเมื่ออ่านเสร็จ
    with open(filename, "r", encoding="utf-8") as file:
        # csv.reader แยกแต่ละบรรทัดออกเป็น list ของค่าตาม comma
        reader = csv.reader(file)

        # วนอ่านข้อมูลทีละแถว ไม่อ่านทั้งหมดทีเดียวเพื่อให้เข้าใจขั้นตอนได้ง่าย
        for row in reader:
            # ข้ามบรรทัดว่าง ถ้ามีอยู่ในไฟล์ข้อมูล
            if len(row) == 0:
                continue

            # งานนี้กำหนดให้แต่ละแถวมี 32 ค่า
            if len(row) != 32:
                raise ValueError("ข้อมูลหนึ่งแถวต้องมี 32 ค่า")

            # เก็บ ID ไว้อ้างอิง แต่ไม่ส่งเข้า MLP เพราะ ID ไม่ใช่ feature
            sample_id = row[0]

            # แปลง class ให้เป็นตัวเลข
            if row[1] == "M":
                answer = 1
            else:
                answer = 0

            # ค่า feature อยู่ตั้งแต่ตำแหน่งที่ 3 ถึง 32
            features = []
            for value in row[2:]:
                features.append(float(value))

            # เก็บข้อมูลหนึ่งแถวให้เป็นก้อนเดียวกัน
            data.append({"id": sample_id, "answer": answer, "features": features})

    return data


def get_min_max(data):
    """หาค่า minimum และ maximum ของ feature แต่ละคอลัมน์

    การหาค่านี้จะทำจาก training set เท่านั้น เพื่อไม่ให้ข้อมูลของ test set
    แอบเข้าไปช่วยการฝึกเครือข่าย เรียกว่าเป็นการป้องกัน data leakage
    """
    # ใช้ len ของ feature แถวแรกเพื่อรู้ว่ามีทั้งหมดกี่คอลัมน์
    number_of_features = len(data[0]["features"])
    minimum = []
    maximum = []

    # ทำทีละคอลัมน์ เพราะแต่ละ feature มีหน่วยและช่วงค่าไม่เท่ากัน
    for feature_number in range(number_of_features):
        values = []

        # ดึงค่าของ feature คอลัมน์เดียวกันจากทุก sample
        for sample in data:
            values.append(sample["features"][feature_number])

        # เก็บค่าต่ำสุดและสูงสุดของคอลัมน์นั้นไว้ใช้ normalize
        minimum.append(min(values))
        maximum.append(max(values))

    return minimum, maximum


def normalize(data, minimum, maximum):
    """ปรับ feature ให้อยู่ประมาณช่วง 0 ถึง 1 ด้วย min-max scaling

    สูตรที่ใช้คือ (ค่าเดิม - ค่าต่ำสุด) / (ค่าสูงสุด - ค่าต่ำสุด)
    การ normalize สำคัญเพราะถ้า feature บางตัวมีค่าหลักพัน
    feature นั้นจะมีอิทธิพลต่อ weighted sum มากเกินไป
    """
    new_data = []

    for sample in data:
        new_features = []

        # enumerate ให้ทั้งตำแหน่ง index และค่าของ feature
        for index, value in enumerate(sample["features"]):
            low = minimum[index]
            high = maximum[index]

            # ถ้า feature มีค่าเท่ากันหมด จะไม่สามารถหารด้วยช่วงได้
            # ในกรณีนี้ให้กำหนดค่าเป็น 0 ไปเลย
            if high == low:
                scaled_value = 0.0
            else:
                # สูตร min-max scaling ทำให้ low กลายเป็น 0 และ high กลายเป็น 1
                scaled_value = (value - low) / (high - low)

            new_features.append(scaled_value)

        # สร้าง dictionary ใหม่แทนการแก้ข้อมูลเดิม
        # ทำให้ยังมีข้อมูลดิบไว้ตรวจสอบได้ถ้าจำเป็น
        new_data.append({
            "id": sample["id"],
            "answer": sample["answer"],
            "features": new_features,
        })

    return new_data


def make_folds(data, number_of_folds=10, seed=2026):
    """แบ่งข้อมูลเป็น folds แบบรักษาสัดส่วนของแต่ละ class

    10-fold cross-validation หมายถึงแบ่งข้อมูลเป็น 10 ส่วน
    รอบที่ 1 ใช้ส่วนที่ 1 เป็น test และอีก 9 ส่วนเป็น train
    รอบที่ 2 ใช้ส่วนที่ 2 เป็น test และทำแบบนี้จนครบ 10 รอบ

    การแบ่งแบบ stratified ทำให้ทุก fold มี B และ M ใกล้เคียงกัน
    """
    # สร้าง random object แยกต่างหาก และกำหนด seed ให้ผลทำซ้ำได้
    # ถ้าใช้ seed เดิม การแบ่ง folds จะเหมือนเดิมทุกครั้ง
    random_generator = random.Random(seed)
    benign = []
    malignant = []

    # แยก B และ M ก่อน เพื่อให้กระจายแต่ละ class ไปทุก fold
    for sample in data:
        if sample["answer"] == 0:
            benign.append(sample)
        else:
            malignant.append(sample)

    # สุ่มลำดับก่อนแจก เพื่อไม่ให้ข้อมูลที่เรียงติดกันอยู่ fold เดียวกัน
    random_generator.shuffle(benign)
    random_generator.shuffle(malignant)
    # สร้าง list ว่างจำนวน 10 ช่อง เช่น [[], [], ..., []]
    folds = [[] for _ in range(number_of_folds)]

    # แจกข้อมูลของแต่ละ class แบบวนรอบทีละ fold
    # index % number_of_folds ทำให้แจกวนจาก fold 0 ถึง fold 9
    for index, sample in enumerate(benign):
        folds[index % number_of_folds].append(sample)
    for index, sample in enumerate(malignant):
        folds[index % number_of_folds].append(sample)

    # สลับลำดับภายในแต่ละ fold อีกครั้ง
    for fold in folds:
        random_generator.shuffle(fold)

    return folds


# -----------------------------------------------------------------------------
# ส่วนที่ 2: ฟังก์ชันพื้นฐานของ MLP
# -----------------------------------------------------------------------------
def sigmoid(value):
    """ฟังก์ชัน activation ที่ให้ค่าอยู่ระหว่าง 0 ถึง 1

    sigmoid(x) = 1 / (1 + e ยกกำลัง -x)
    ค่าใกล้ 1 หมายถึง network เชื่อว่าเป็น class M
    ค่าใกล้ 0 หมายถึง network เชื่อว่าเป็น class B
    """
    # ป้องกัน math.exp ทำงานกับตัวเลขที่มากเกินไป
    if value < -40:
        return 0.0
    if value > 40:
        return 1.0
    return 1.0 / (1.0 + math.exp(-value))


def count_weights(network):
    """คำนวณจำนวนยีนทั้งหมดของ chromosome ตามโครงสร้าง network

    ตัวอย่าง [30, 8, 1]
    - จาก input 30 ไป hidden 8 มี (30 + 1) * 8 น้ำหนัก
    - จาก hidden 8 ไป output 1 มี (8 + 1) * 1 น้ำหนัก
    - +1 ในแต่ละชั้นคือ bias ของ neuron
    """
    # total คือความยาวของ chromosome ที่ต้องสร้าง
    total = 0

    # network เช่น [30, 8, 1] มีการเชื่อมต่อ 2 ชุด
    for layer_number in range(len(network) - 1):
        input_nodes = network[layer_number]
        output_nodes = network[layer_number + 1]
        # neuron แต่ละตัวรับน้ำหนักจาก input ทุกตัว และมี bias อีก 1 ค่า
        total += (input_nodes + 1) * output_nodes

    return total


def chromosome_to_matrices(chromosome, network):
    """เปลี่ยน chromosome ยาว ๆ ให้เป็นตารางน้ำหนักของแต่ละ layer

    GA มองน้ำหนักทั้งหมดเป็น list เดียวเพื่อให้ง่ายต่อการ crossover
    แต่ตอนคำนวณ MLP ต้องแบ่งกลับเป็น matrix ของแต่ละ layer
    """
    matrices = []
    # position บอกว่าตอนนี้อ่าน chromosome ไปถึงยีนที่เท่าไรแล้ว
    position = 0

    for layer_number in range(len(network) - 1):
        input_nodes = network[layer_number]
        output_nodes = network[layer_number + 1]
        # 1 แถวแทน neuron 1 ตัว และมีน้ำหนัก input + bias
        width = input_nodes + 1
        matrix = []

        for _ in range(output_nodes):
            # ตัดยีนตามจำนวนที่ layer นี้ต้องใช้
            row = chromosome[position:position + width]
            matrix.append(row)
            position += width

        matrices.append(matrix)

    return matrices


def forward(matrices, input_values):
    """ส่งข้อมูลหนึ่งตัวอย่างผ่าน MLP แล้วคืนค่า output

    การทำงานของ neuron คือ
    1. นำ input คูณ weight ของตัวเอง
    2. บวกค่าทั้งหมดรวมกับ bias
    3. ส่งผลผ่าน sigmoid
    4. ใช้ผลลัพธ์เป็น input ให้ layer ถัดไป
    """
    values = list(input_values)

    # วนทีละ layer ตั้งแต่ input ไป output
    for matrix in matrices:
        next_values = []

        # วนคำนวณทีละ neuron ใน layer ปัจจุบัน
        for neuron_weights in matrix:
            # น้ำหนักตัวสุดท้ายเป็น bias
            total = neuron_weights[-1]

            # คูณ input กับน้ำหนัก แล้วบวกกัน
            for index in range(len(values)):
                total += values[index] * neuron_weights[index]

            # activation ของ neuron นี้จะถูกส่งต่อไป layer ถัดไป
            next_values.append(sigmoid(total))

        values = next_values

    # งานนี้มี output neuron เพียง 1 ตัว
    return values[0]


def check_network(chromosome, network, data):
    """ทดสอบ network กับข้อมูล และคำนวณค่าต่าง ๆ

    probability คือ output จริงของ sigmoid
    predicted คือ class ที่ตัดสินหลังใช้ threshold 0.5
    จากนั้นนับ TP, TN, FP, FN เพื่อนำไปคำนวณ metric ต่าง ๆ
    """
    matrices = chromosome_to_matrices(chromosome, network)
    correct = 0
    sum_squared_error = 0.0
    true_positive = 0
    true_negative = 0
    false_positive = 0
    false_negative = 0

    for sample in data:
        probability = forward(matrices, sample["features"])
        # ถ้า output ตั้งแต่ 0.5 ขึ้นไป ให้ตัดสินเป็น M
        predicted = 1 if probability >= 0.5 else 0
        answer = sample["answer"]

        if predicted == answer:
            correct += 1

        # MSE ดูว่าค่า probability ห่างจากคำตอบจริงมากแค่ไหน
        sum_squared_error += (probability - answer) ** 2

        if predicted == 1 and answer == 1:
            true_positive += 1
        elif predicted == 0 and answer == 0:
            true_negative += 1
        elif predicted == 1 and answer == 0:
            false_positive += 1
        elif predicted == 0 and answer == 1:
            false_negative += 1

    # total ใช้เป็นตัวหารเพื่อเปลี่ยนจำนวนถูกต้องเป็นสัดส่วน
    total = len(data)
    sensitivity_denominator = true_positive + false_negative
    specificity_denominator = true_negative + false_positive

    # sensitivity = ตรวจ malignant ได้ถูกต้องกี่ส่วน
    # specificity = ตรวจ benign ได้ถูกต้องกี่ส่วน
    return {
        "accuracy": correct / total,
        "mse": sum_squared_error / total,
        "sensitivity": true_positive / sensitivity_denominator if sensitivity_denominator else 0,
        "specificity": true_negative / specificity_denominator if specificity_denominator else 0,
        "tp": true_positive,
        "tn": true_negative,
        "fp": false_positive,
        "fn": false_negative,
    }


# -----------------------------------------------------------------------------
# ส่วนที่ 3: Genetic Algorithm
# -----------------------------------------------------------------------------
def random_chromosome(length, random_generator):
    """สร้าง chromosome เริ่มต้นด้วยค่าน้ำหนักสุ่มช่วง -2 ถึง 2

    chromosome 1 ตัวเปรียบเสมือน network 1 แบบ
    แต่ละตำแหน่งใน list คือ weight หรือ bias 1 ค่า
    """
    chromosome = []
    for _ in range(length):
        chromosome.append(random_generator.uniform(-2.0, 2.0))
    return chromosome


def get_fitness(chromosome, network, data):
    """คำนวณคะแนนของ chromosome

    GA ต้องมีตัวเลข 1 ค่าไว้เปรียบเทียบว่า chromosome ไหนดีกว่า
    งานนี้ใช้ accuracy เป็นคะแนนหลัก และลบ MSE เล็กน้อยเพื่อให้
    กรณีที่ accuracy เท่ากัน เลือกตัวที่ให้ probability ใกล้คำตอบกว่า
    """
    result = check_network(chromosome, network, data)
    return result["accuracy"] - 0.05 * result["mse"]


def choose_parent(population, scores, random_generator):
    """เลือก parent ด้วย tournament selection

    สุ่มสมาชิก 3 ตัวจากประชากร แล้วเลือกตัวที่มี fitness สูงที่สุด
    วิธีนี้เข้าใจง่ายและยังเปิดโอกาสให้ chromosome อื่น ๆ ได้ถูกเลือกบ้าง
    """
    # เก็บตำแหน่งของสมาชิกที่สุ่มมา ไม่ได้เก็บคะแนนโดยตรง
    candidate_indexes = []
    for _ in range(3):
        candidate_indexes.append(random_generator.randrange(len(population)))

    # เริ่มต้นให้คนแรกเป็นผู้ชนะ แล้วเปรียบเทียบกับคนต่อไป
    best_index = candidate_indexes[0]
    for index in candidate_indexes[1:]:
        if scores[index] > scores[best_index]:
            best_index = index

    return population[best_index]


def crossover(parent_a, parent_b, random_generator):
    """ผสมยีนของ parent สองตัวด้วยค่าเฉลี่ยแบบสุ่ม

    ถ้า ratio ใกล้ 1 ลูกจะคล้าย parent_a
    ถ้า ratio ใกล้ 0 ลูกจะคล้าย parent_b
    การทำแบบนี้ใช้กับ weight ที่เป็นตัวเลขต่อเนื่องได้โดยตรง
    """
    child = []

    # ต้องวนครบทุกยีน เพราะ weight ทุกตัวมีผลต่อ network
    for index in range(len(parent_a)):
        mixing_ratio = random_generator.random()
        value = (mixing_ratio * parent_a[index]) + ((1 - mixing_ratio) * parent_b[index])
        child.append(value)

    return child


def mutate(chromosome, random_generator):
    """สุ่มเปลี่ยนน้ำหนักบางตัวเพื่อให้ประชากรค้นหาคำตอบใหม่ได้

    mutation ทำหน้าที่ช่วยไม่ให้ประชากรเหมือนกันหมดเร็วเกินไป
    ถ้าไม่มี mutation อาจติดอยู่ที่คำตอบเฉพาะบริเวณเดิม
    """
    child = list(chromosome)
    # mutation_rate = โอกาสที่ยีนแต่ละตัวจะถูกเปลี่ยน
    mutation_rate = 0.08

    for index in range(len(child)):
        if random_generator.random() < mutation_rate:
            # gauss(0, 0.25) ให้ค่าบวกหรือลบเล็กน้อยแบบสุ่ม
            child[index] += random_generator.gauss(0, 0.25)

            # จำกัดน้ำหนักไม่ให้โตมากจน sigmoid อิ่มตัวเร็วเกินไป
            if child[index] > 5:
                child[index] = 5
            if child[index] < -5:
                child[index] = -5

    return child


def train_network(train_data, network, seed):
    """ฝึก network หนึ่งตัวด้วย Genetic Algorithm

    ลำดับการทำงานในแต่ละ generation คือ
    1. ประเมิน fitness ของสมาชิกทุกตัว
    2. หาตัวที่ดีที่สุด
    3. เก็บตัวที่ดีที่สุดไว้ด้วย elitism
    4. เลือก parent, crossover และ mutation เพื่อสร้างสมาชิกใหม่
    5. ใช้ประชากรใหม่เริ่ม generation ถัดไป
    """
    # ใช้ seed แยกตาม fold เพื่อให้ทดลองซ้ำได้และแต่ละ fold ไม่สุ่มเหมือนกันหมด
    random_generator = random.Random(seed)
    # population_size คือจำนวน chromosome ใน 1 generation
    population_size = 16
    # number_of_generations คือจำนวนรอบที่ GA จะพัฒนาประชากร
    number_of_generations = 20
    # จำนวนยีนต้องพอดีกับน้ำหนักและ bias ของ network
    chromosome_size = count_weights(network)

    population = []
    # สร้างประชากรเริ่มต้นจากน้ำหนักสุ่ม
    for _ in range(population_size):
        population.append(random_chromosome(chromosome_size, random_generator))

    best_chromosome = None
    best_score = -999

    # generation ไม่ได้ใช้คำนวณโดยตรง แต่ช่วยบอกว่าอยู่รอบที่เท่าไร
    for generation in range(number_of_generations):
        scores = []

        # ทุก chromosome ต้องถูกนำไปลองกับ train data เพื่อหาคะแนน
        for chromosome in population:
            scores.append(get_fitness(chromosome, network, train_data))

        # เก็บตัวที่ดีที่สุดของ generation นี้ไว้ก่อน
        best_index = 0
        for index in range(1, len(population)):
            if scores[index] > scores[best_index]:
                best_index = index

        if scores[best_index] > best_score:
            best_score = scores[best_index]
            best_chromosome = list(population[best_index])

        # เรียงลำดับ population จาก fitness สูงไปต่ำ
        # สร้างคู่ (คะแนน, chromosome) แล้วเรียงจากมากไปน้อย
        ranked = []
        for index in range(len(population)):
            ranked.append((scores[index], population[index]))
        ranked.sort(key=lambda item: item[0], reverse=True)

        # elitism: ยกตัวที่ดีที่สุด 2 ตัวไป generation ถัดไปโดยไม่เปลี่ยน
        new_population = [list(ranked[0][1]), list(ranked[1][1])]

        # สร้างลูกเพิ่มจนกว่าจะมีจำนวนครบเท่าประชากรเดิม
        while len(new_population) < population_size:
            parent_a = choose_parent(population, scores, random_generator)
            parent_b = choose_parent(population, scores, random_generator)
            child = crossover(parent_a, parent_b, random_generator)
            child = mutate(child, random_generator)
            new_population.append(child)

        population = new_population

    return best_chromosome, best_score


# -----------------------------------------------------------------------------
# ส่วนที่ 4: ทดลองหลาย configuration และเขียนผลลัพธ์
# -----------------------------------------------------------------------------
def run_experiment(data):
    """ทดลองทุก configuration ด้วย 10-fold cross-validation

    ในแต่ละ fold จะสร้าง network และฝึกใหม่ตั้งแต่ต้น
    เพราะห้ามให้ network ที่ฝึกจาก fold ก่อนหน้าไหลมาช่วย fold ถัดไป
    """
    # แบ่งข้อมูลครั้งเดียว แล้วสลับ fold ที่เป็น test ไปทีละ fold
    folds = make_folds(data, 10)
    # [8] หมายถึง hidden layer 1 ชั้น มี 8 nodes
    # [8, 8] หมายถึง hidden layer 2 ชั้น ชั้นละ 8 nodes
    configurations = [[8], [16], [8, 8], [12, 6]]
    records = []

    for configuration_number, hidden_layers in enumerate(configurations, start=1):
        # 30 input nodes และ 1 output node ถูกกำหนดไว้ตามข้อมูลของงาน
        network = [30] + hidden_layers + [1]
        name = "-".join(str(node) for node in hidden_layers)
        print("\\nConfiguration:", name, "network =", network)

        # ทำให้ครบ 10 รอบ เพื่อให้ทุก fold ได้ทำหน้าที่เป็น test 1 ครั้ง
        for test_fold_number in range(10):
            test_data = folds[test_fold_number]
            train_data = []

            # รวมอีก 9 folds เป็น training data
            for fold_number in range(10):
                if fold_number != test_fold_number:
                    train_data.extend(folds[fold_number])

            # normalize โดยใช้ train data ของรอบนั้นเท่านั้น
            minimum, maximum = get_min_max(train_data)
            train_scaled = normalize(train_data, minimum, maximum)
            test_scaled = normalize(test_data, minimum, maximum)

            # จับเวลาเฉพาะการฝึกและการทดสอบของ fold นี้
            start_time = time.time()
            seed = 9000 + configuration_number * 100 + test_fold_number
            chromosome, train_fitness = train_network(train_scaled, network, seed)
            train_result = check_network(chromosome, network, train_scaled)
            test_result = check_network(chromosome, network, test_scaled)
            seconds = time.time() - start_time

            # เก็บผลเป็น dictionary เพื่อเขียนลง CSV ได้ง่าย
            record = {
                "configuration": name,
                "hidden_layers": len(hidden_layers),
                "nodes": "+".join(str(node) for node in hidden_layers),
                "fold": test_fold_number + 1,
                "train_accuracy": train_result["accuracy"],
                "test_accuracy": test_result["accuracy"],
                "test_sensitivity": test_result["sensitivity"],
                "test_specificity": test_result["specificity"],
                "test_mse": test_result["mse"],
                "tp": test_result["tp"],
                "tn": test_result["tn"],
                "fp": test_result["fp"],
                "fn": test_result["fn"],
                "best_fitness": train_fitness,
                "seconds": seconds,
            }
            records.append(record)
            print(" fold", test_fold_number + 1, "accuracy =", round(record["test_accuracy"], 4))

    return records


def make_summary(records):
    """หาค่าเฉลี่ยและส่วนเบี่ยงเบนมาตรฐานของแต่ละ configuration

    ค่าเฉลี่ยบอก performance โดยรวม ส่วน standard deviation บอกว่า
    ผลของแต่ละ fold กระจายมากน้อยแค่ไหน
    """
    summaries = []
    names = ["8", "16", "8-8", "12-6"]

    for name in names:
        # เลือกเฉพาะผลที่มาจาก configuration เดียวกัน
        selected = []
        for record in records:
            if record["configuration"] == name:
                selected.append(record)

        # statistics.mean ใช้หาค่าเฉลี่ยของผลทั้ง 10 folds
        summaries.append({
            "configuration": name,
            "folds": len(selected),
            "accuracy_mean": statistics.mean(r["test_accuracy"] for r in selected),
            "accuracy_stdev": statistics.stdev(r["test_accuracy"] for r in selected),
            "sensitivity_mean": statistics.mean(r["test_sensitivity"] for r in selected),
            "specificity_mean": statistics.mean(r["test_specificity"] for r in selected),
            "mse_mean": statistics.mean(r["test_mse"] for r in selected),
            "seconds_mean": statistics.mean(r["seconds"] for r in selected),
        })

    return summaries


def save_results(records, summaries):
    """บันทึกผลราย fold และผลสรุปไว้ในไฟล์ CSV

    ส่วนแรกของไฟล์เป็นผลละเอียดทีละ fold
    ส่วนท้ายหลังคำว่า summary เป็นค่าเฉลี่ยของแต่ละ configuration
    """
    fieldnames = list(records[0].keys())

    with open(RESULT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        # เขียนชื่อคอลัมน์ก่อน แล้วจึงเขียนข้อมูลแต่ละแถว
        writer.writeheader()
        writer.writerows(records)

        # เว้นบรรทัด แล้วเขียนส่วน summary ต่อท้ายไฟล์เดียวกัน
        file.write("\\n")
        summary_writer = csv.writer(file)
        summary_writer.writerow(["summary"])
        summary_writer.writerow(["configuration", "folds", "accuracy_mean", "accuracy_stdev", "sensitivity_mean", "specificity_mean", "mse_mean", "seconds_mean"])

        for summary in summaries:
            summary_writer.writerow([
                summary["configuration"], summary["folds"], summary["accuracy_mean"],
                summary["accuracy_stdev"], summary["sensitivity_mean"],
                summary["specificity_mean"], summary["mse_mean"], summary["seconds_mean"],
            ])


def main():
    """จุดเริ่มต้นของโปรแกรม

    ฟังก์ชัน main ทำหน้าที่เรียกลำดับงานทั้งหมด
    ทำให้เมื่ออ่านโค้ดจากล่างขึ้นบนจะเห็น flow ของโปรแกรมได้ง่าย
    """
    # ขั้นที่ 1: อ่านข้อมูลจากไฟล์
    data = read_data(DATA_FILE)
    benign_count = sum(sample["answer"] == 0 for sample in data)
    malignant_count = sum(sample["answer"] == 1 for sample in data)

    print("จำนวนข้อมูลทั้งหมด:", len(data))
    print("จำนวน features:", len(data[0]["features"]))
    print("Benign:", benign_count, "Malignant:", malignant_count)

    # ขั้นที่ 2: ฝึกและทดสอบทุก configuration
    records = run_experiment(data)
    # ขั้นที่ 3: สรุปผลจาก 10 folds
    summaries = make_summary(records)
    # ขั้นที่ 4: บันทึกผลลงไฟล์ CSV
    save_results(records, summaries)

    print("\\nผลสรุป 10-fold cross-validation")
    print("configuration | accuracy | sensitivity | specificity | mse")
    for summary in summaries:
        print(
            summary["configuration"], "|",
            round(summary["accuracy_mean"], 4), "|",
            round(summary["sensitivity_mean"], 4), "|",
            round(summary["specificity_mean"], 4), "|",
            round(summary["mse_mean"], 5),
        )

    print("\\nบันทึกผลลัพธ์ไว้ที่:", RESULT_FILE)


if __name__ == "__main__":
    main()
