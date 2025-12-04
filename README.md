# Dự án Phân Tích Mạng Petri

Dự án này cung cấp một module để phân tích các mạng Petri 1-safe bằng nhiều kỹ thuật khác nhau. Toàn bộ được chia thành nhiều tác vụ, mỗi tác vụ được triển khai trong một module riêng nhằm đảm bảo rõ ràng và dễ mở rộng.

## Cấu Trúc Dự Án

```
requirements.txt
Task1_Parser/
    task1.py           # Bộ phân tích PetriNet (PNML, trọng số)
Task2_Explicit/
    task2.py           # Duyệt không gian trạng thái theo phương pháp tường minh
Task3_BDD/
    task3.py           # Phân tích khả đạt sử dụng BDD
Task4_Deadlock/
    task4.py           # Phát hiện deadlock (ILP + BDD)
Task5_Optimization/
    task5.py           # Tối ưu hóa trên tập marking khả đạt
Test_PNML_Files/
    config1.pnml       # File PNML ví dụ
main.py                # Chương trình tổng hợp kiểm thử cho tất cả tác vụ
```

## Tổng Quan Các Tác Vụ

### **Task 1: Parser**

* Phân tích các file PNML và trích xuất cấu trúc mạng Petri cùng các trọng số.

### **Task 2: Duyệt tường minh**

* Tính toán toàn bộ tập marking khả đạt bằng tìm kiếm trạng thái tường minh.

### **Task 3: Tính toán ký hiệu bằng BDD**

* Sử dụng Binary Decision Diagrams (BDD) để biểu diễn và phân tích hiệu quả các trạng thái khả đạt.

### **Task 4: Phát hiện deadlock**

* Phát hiện trạng thái deadlock bằng ILP kết hợp với BDD.

### **Task 5: Tối ưu hóa**

* Tìm marking khả đạt tối ưu dựa trên trọng số do người dùng định nghĩa hoặc đọc từ file.

## Cách Chạy

1. **Cài đặt thư viện phụ thuộc:**

   ```powershell
   pip install -r requirements.txt
   winget install graphviz
   ```

2. **Chạy chương trình kiểm thử chính:**

   ```powershell
   python main.py <pnml_file>
   ```
    Trong đó `<pnml_file>` là đường dẫn tới file PNML bạn muốn phân tích. Nếu không cung cấp, chương trình sẽ sử dụng file ví dụ `Test_PNML_Files/config1.pnml`.

   Lệnh này sẽ phân tích file PNML ví dụ, chạy tất cả các tác vụ phân tích và in kết quả ra console. Ngoài ra, có thư mục logs/ để lưu các output cho dễ theo dõi. Thư mục bdd_visualizations/ sẽ chứa các file hình ảnh minh họa cấu trúc BDD.

## Thêm File PNML Mới

* Đặt các file `.pnml` của bạn vào thư mục `Test_PNML_Files/`.
* Chạy python main.py <your_pnml_file> để phân tích file của bạn.

## Yêu Cầu

* Python 3.8+
* Các thư viện quan trọng: `dd` (BDD), `pulp` (ILP), `numpy`, `xml.etree.ElementTree`, `graphviz`

## Tác Giả

* Trần Văn Thiên Kim: BDD reachability
* Lê Đức Nguyên Khoa: Parser PNML và duyệt tường minh
* Nguyễn Trà My: Tối ưu hóa
* Nguyễn Hồng Phúc: Phát hiện deadlock
* Phan Phước Thiện Quang: BDD reachability

## API Reference 

### 🛠️ Task 1: Khởi tạo & Xử lý Dữ liệu (Parsing & Weights)

Nhiệm vụ này tập trung vào việc thiết lập môi trường, đọc dữ liệu đầu vào và xây dựng cấu trúc mạng cơ bản.

### 🕸️ Class `PetriNet`

Class này chịu trách nhiệm phân tích file cấu trúc PNML, mô hình hóa mạng Petri dưới dạng ma trận 🔢 và thực hiện tính toán các trạng thái khả đạt (*reachable markings*) bằng phương pháp duyệt đồ thị tường minh 🗺️ (**Explicit State Space Exploration**).

#### 🧩 `__init__(self, pnml_file_path)`

**Chức năng:**

* 🏗️ Khởi tạo đối tượng mạng Petri.
* 🗑️ Thiết lập các cấu trúc dữ liệu rỗng (`Places`, `Transitions`, `Ma trận liên thuộc`).
* 🔄 Tự động gọi phương thức `read_pnml_file` để nạp dữ liệu từ đường dẫn được cung cấp.

**Tham số:**

* `pnml_file_path`: Đường dẫn đến file `.pnml` chứa cấu trúc mạng Petri.

#### 📄 `read_pnml_file(self, file_path: str)`

Phân tích cú pháp file XML (định dạng PNML) để xây dựng mô hình toán học của mạng.

**Chức năng:**

* 🌲 Sử dụng thư viện `xml.etree.ElementTree` để duyệt cây XML.
* 📍 Trích xuất danh sách **Places** và **Initial Marking** (trạng thái ban đầu).
* ⚡ Trích xuất danh sách **Transitions**.
* 🧱 Xây dựng hai ma trận trọng số cơ bản:
    * `self.pre_matrix`: Ma trận đầu vào (Place $\to$ Transition).
    * `self.post_matrix`: Ma trận đầu ra (Transition $\to$ Place).

**Tham số:**

* `file_path`: Đường dẫn tuyệt đối hoặc tương đối đến file `.pnml`.

#### ⚖️ `read_weight(self, weight_file_path)`

Đọc dữ liệu trọng số cho các Place từ file văn bản bên ngoài (phục vụ cho các bài toán tối ưu hóa).

**Chức năng:**

* 📥 Đọc file text chứa các số nguyên (cách nhau bởi khoảng trắng hoặc xuống dòng).
* 🔢 Chuyển đổi dữ liệu thành mảng NumPy (`self.c`).
* ✅ Kiểm tra tính hợp lệ: Số lượng trọng số trong file phải khớp với số lượng Place trong mạng (`self.num_places`).

**Tham số:**

* `weight_file_path`: Đường dẫn đến file chứa trọng số.

---

### 🚀 Task 2: Tính toán Không gian Trạng thái (State Space Computation)

Nhiệm vụ này thực hiện các thuật toán cốt lõi để khám phá, tính toán và hiển thị không gian trạng thái của mạng.

#### 🧠 `explicit_reachable_markings_computation(self, method="bfs")`

Thực hiện thuật toán duyệt đồ thị để tìm kiếm toàn bộ không gian trạng thái khả đạt từ trạng thái ban đầu ($M_0$).

**Chức năng:**

* 🔍 Hỗ trợ hai chiến lược duyệt: **BFS** (Breadth-First Search) và **DFS** (Depth-First Search).
* 🚦 Kiểm tra điều kiện kích hoạt (enable) của transition: $M \ge Pre$.
* 🧮 Tính toán trạng thái mới theo công thức: $M_{new} = M - Pre + Post$.
* ⏱️ **Cơ chế Timeout:** Tự động dừng và trả về lỗi nếu thời gian thực thi vượt quá 10 giây.

**Tham số:**

* `method` (str): Phương pháp duyệt, chấp nhận `"bfs"` hoặc `"dfs"`. Mặc định là `"bfs"`.

**Trả về:** tuple gồm:

* `marking_states` (list): Danh sách các vector trạng thái (markings) tìm thấy. (Trả về `-1` nếu timeout).
* `elapsed_time` (float): Thời gian thực thi thuật toán tính bằng giây.

#### 💻 `print_reachable_markings(self, method="bfs")`

Hàm tiện ích dùng để thực thi thuật toán và in kết quả ra màn hình console theo định dạng dễ đọc.

**Chức năng:**

* 📞 Gọi hàm `explicit_reachable_markings_computation`.
* 📊 Hiển thị tổng số trạng thái và thời gian thực thi.
* 📝 Liệt kê chi tiết từng vector trạng thái tìm được.

**Tham số:**

* `method` (str): Phương pháp duyệt, `"bfs"` hoặc `"dfs"`. Mặc định là `"bfs"`.

**Đầu ra ví dụ:**

```text
Total states found: 3
Execution time: 0.000000 seconds
----------------------------------------
Reachable marking states
----------------------------------------
[1, 0, 0]
[0, 1, 0]
[0, 0, 1]
```

---

### 🌳 Task 3: Phân tích bằng BDD (Reachability & Optimization)

Nhiệm vụ này sử dụng cấu trúc dữ liệu **Binary Decision Diagrams (BDD)** để biểu diễn và xử lý không gian trạng thái khổng lồ một cách hiệu quả, đồng thời hỗ trợ tìm kiếm trạng thái tối ưu.

### Class `BDD_Reachability`

Class này cung cấp các phương thức cốt lõi để xây dựng logic chuyển đổi và phân tích trạng thái mạng Petri trên nền tảng BDD.

#### ⚙️ `__init__(self, petri_net: PetriNet)`

**Chức năng:**

* Khởi tạo đối tượng solver và thiết lập môi trường BDD.
* Tự động khai báo các cặp biến BDD cho mỗi Place:

  * `x_p`: Biến đại diện cho trạng thái hiện tại.
  * `y_p`: Biến đại diện cho trạng thái tiếp theo sau khi bắn transition.

**Tham số:**

* `petri_net`: Đối tượng chứa cấu trúc mạng Petri (Places, Transitions và các ma trận liên thuộc).

#### 🌉 `build_transition(self)`

Xây dựng BDD khổng lồ đại diện cho **quan hệ chuyển đổi toàn cục** ($R_{total}$) của mạng.

**Chức năng:**

* 🔄 Duyệt qua từng transition trong mạng.

* 🔗 Tự động phát hiện Input arcs và Output arcs.

* 🚦 Xây dựng logic **Enable** (điều kiện kích hoạt) và **Update** (cập nhật token).

* 🖼️ Áp dụng **Frame Axiom** cho các Place không tham gia transition (giữ nguyên giá trị token).

#### 🔄 `compute_reachable_states(self)`

Thực hiện vòng lặp **fixed-point iteration** để tính toàn bộ tập trạng thái khả đạt từ trạng thái ban đầu.

**Trả về:** tuple gồm:

* `current_states` (BDD Object): Đối tượng BDD biểu diễn tập trạng thái.

* `total_states` (int): Số lượng trạng thái tìm thấy.

* `time` (float): Thời gian thực thi tính toán.

#### 🖨️ `print_reachable_states_list(self, states_bdd)`

Hàm tiện ích dùng để "giải nén" node BDD và in ra danh sách markings dưới dạng dictionary dễ đọc.

**Đầu ra ví dụ:**

```
{'p1': 1, 'p2': 0, 'p3': 1}
```

---


#### 🧬 `get_expr_from_bdd(self, bdd_node) -> str`

Trích xuất công thức logic từ một node BDD.

**Trả về:** Chuỗi ký tự dạng `ite(...)` (If-Then-Else).

**Mục đích:**

* Phân tích cấu trúc logic bên trong BDD.
* Hữu ích khi debug hoặc ghi log.

* 🐛 Hữu ích khi debug hoặc ghi log kiểm tra lỗi.

### 🔒 Task 4: Phát hiện Deadlock (Hybrid ILP + BDD)

Nhiệm vụ này triển khai thuật toán phát hiện Deadlock thông minh bằng cách kết hợp sức mạnh của **Integer Linear Programming (ILP)** và **BDD**.

### Class `ILP_BDD_Deadlock_Detection`

**Ý tưởng chính:**

* 🐣 **Mạng nhỏ:** Kiểm tra toàn bộ trạng thái reachable bằng ILP (độ chính xác tuyệt đối).

* 🦖 **Mạng vừa/lớn:** Dùng BDD để lọc nhanh các marking nghi ngờ là deadlock, sau đó xác minh lại bằng ILP để đảm bảo tính đúng đắn.

#### 🏗️ `__init__(...)`

Khởi tạo bộ phát hiện deadlock và xây dựng mô hình toán học nền tảng.

**Chức năng:**

* 🔗 Liên kết thông tin từ `PetriNet` và `BDD` vào ILP framework.

* 📐 Xây dựng mô hình ILP gồm:

  * Biến nhị phân `e_t` cho mỗi transition (transition $t$ có enabled hay không).

  * Các ràng buộc (constraints) tương ứng cho mỗi transition.

* 📏 Thiết lập các giới hạn cấu trúc (marking limit, place limit...) để tự động chọn chiến lược tìm kiếm phù hợp.

**Tham số:**

* `petri_net`, `bdd_reach`: Các đối tượng dữ liệu đầu vào.

* `marking_limit`, `place_limit`, `transition_limit`: Các ngưỡng để phân loại kích thước mạng.

#### 🔄 `_state_to_marking(self, state)`

Chuyển đổi định dạng dữ liệu từ nghiệm BDD sang Dictionary Marking tiêu chuẩn.

**Chức năng:**

* Nhận input: `{'x_p1': 1, 'x_p2': 0}`.

* Trả về output: `{'p1': 1, 'p2': 0}`.

#### 🕵️‍♂️ `_is_deadlock_ilp(self, marking)`

Kiểm tra một marking cụ thể có phải là deadlock hay không bằng cách giải mô hình ILP.

**Chức năng:**

* 🧮 Tính toán điều kiện kích hoạt cho từng transition dựa trên token hiện có.

* 📉 Giải mô hình ILP để xác định tổng số transition enabled: `enabled_total = Σ(enabled_t)`.

* ✅ Kết luận: Marking là deadlock nếu `enabled_total == 0`.

**Trả về:** `True` nếu là deadlock, ngược lại `False`.

#### 🧱 `_build_dead_bdd(self)`

Xây dựng một BDD biểu diễn tập hợp **tất cả các marking gây ra deadlock** về mặt lý thuyết.

**Chức năng:**

* 1️⃣ Xây dựng logic `enabled` cho từng transition (dựa trên Input Arcs).

* 2️⃣ Tạo biểu thức `enabled_any` bằng cách **OR** tất cả các transition lại.

* 3️⃣ Phủ định biểu thức trên (`NOT enabled_any`) để thu được `dead_bdd` (tập hợp các trạng thái mà không transition nào bắn được).

**Trả về:** Đối tượng `dead_bdd`.

#### 🔍 `find_deadlock(self, states_bdd)`

Hàm điều phối chính để tìm kiếm deadlock trong tập trạng thái khả đạt.

**Chiến lược:**

* **Mạng nhỏ:** Duyệt toàn bộ reachable marking từ BDD, kiểm tra từng cái một với ILP.

* **Mạng lớn:**

  1. Lấy `dead_bdd` từ hàm `_build_dead_bdd`.

  2. Lọc ứng viên: `candidate_bdd = states_bdd AND dead_bdd`.

  3. Chọn mẫu (tối đa 100 nghiệm) từ `candidate_bdd` để xác minh kỹ bằng ILP.

**Trả về:** tuple gồm:

* `marking_deadlock` (dict/None): Deadlock tìm được.

* `duration` (float): Thời gian tìm kiếm.

#### 📢 `print_deadlock(self, deadlock)`

Hàm tiện ích để hiển thị kết quả tìm kiếm deadlock ra màn hình console một cách rõ ràng.

### Task 5: Tối ưu hóa khả năng tiếp cận (Reachable optimization)

### Class `Optimization`

**Ý tưởng chính:**

* ⚡ Dựa trên BDD để duyệt toàn bộ không gian trạng thái khả đạt một cách tối ưu.

* ⚖️ Tối ưu hóa dựa trên trọng số — mỗi trạng thái được đánh điểm bằng tổng trọng số của các place đang có token.

* 🎯 Hỗ trợ ràng buộc: Cho phép giới hạn số token trên từng place để tìm trạng thái "tối ưu hợp lệ".

* 🔄 Tự động đồng bộ trọng số với vector c của Petri net nếu có.

* 🏁 Trả về trạng thái có điểm cao nhất, hoặc điểm cao nhất trong số các trạng thái hợp lệ (nếu có ràng buộc).

### `optimize_reachable_marking(self, reachable_bdd, weights=None)`

Tìm kiếm trạng thái tối ưu trong không gian trạng thái khả đạt dựa trên hệ thống trọng số tùy chỉnh.

**Chức năng:**

* 🕵️‍♂️ Duyệt qua các nghiệm (markings) chứa trong `reachable_bdd` bằng phương thức `pick_iter`.

* ⚖️ Tính toán điểm số (score) cho từng trạng thái theo công thức tổng quát: `score = Σ (has_token × weight)`.

* 🏆 So sánh và lưu giữ trạng thái có **tổng điểm cao nhất**.

**Tham số:**

* `reachable_bdd`: Đối tượng BDD biểu diễn tập hợp các trạng thái khả đạt cần tìm kiếm.

* `weights` (dictionary, tùy chọn): Bảng trọng số cho từng Place (ví dụ: `{'p1': 10, 'p2': -5}`). Mặc định là 1 cho tất cả Places nếu để `None`.

**Trả về:** tuple gồm:

* `best_marking` (dict): Cấu hình trạng thái đạt điểm cao nhất (hoặc `None` nếu không tìm thấy).

* `max_score` (float/int): Điểm số tối ưu tương ứng.

* `duration` (float): Thời gian thực thi quá trình tìm kiếm.

### optimize_with_constraints(self, reachable_bdd, weights=None, constraints=None)

Tối ưu hóa trạng thái khả đạt với ràng buộc đặt trước trên từng Place.

**Chức năng:**

* 🔍 Duyệt qua tất cả trạng thái trong reachable_bdd bằng pick_iter.

* ⚖️ Tính điểm từng trạng thái theo công thức: score = Σ (has_token × weight).

* 🚧 Chỉ chấp nhận các trạng thái thỏa constraints:
– Mỗi constraint là (min, max) cho số token tại một Place.

* 🥇 Lưu lại trạng thái hợp lệ có tổng điểm lớn nhất.

**Tham số:**

* `reachable_bdd`: BDD chứa tập trạng thái khả đạt.

* `weights` (dict, tùy chọn): Trọng số mỗi Place. Mặc định 1 nếu không cung cấp hoặc nếu petri_net.c không dùng được.

* `constraints` (dict, tùy chọn): Ràng buộc dạng { 'p1': (0,1), 'p2': (1,1) }.

**Trả về:** tuple gồm:

* `best_marking` (dict): Trạng thái hợp lệ có điểm cao nhất (hoặc None nếu không có).

* `max_score` (int/float): Điểm tối ưu.

* `duration` (float): Thời gian chạy.

---

## License

Dự án được sử dụng cho mục đích học tập và nghiên cứu.

