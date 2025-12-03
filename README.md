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
   ```

2. **Chạy chương trình kiểm thử chính:**

   ```powershell
   python main.py <pnml_file>
   ```
    Trong đó `<pnml_file>` là đường dẫn tới file PNML bạn muốn phân tích. Nếu không cung cấp, chương trình sẽ sử dụng file ví dụ `Test_PNML_Files/config1.pnml`.

   Lệnh này sẽ phân tích file PNML ví dụ, chạy tất cả các tác vụ phân tích và in kết quả ra console.

## Thêm File PNML Mới

* Đặt các file `.pnml` của bạn vào thư mục `Test_PNML_Files/`.
* Mở và chỉnh sửa `main.py` để trỏ đến file PNML bạn muốn phân tích.

## Yêu Cầu

* Python 3.8+
* Các thư viện quan trọng: `dd` (BDD), `pulp` (ILP), `numpy`, `xml.etree.ElementTree`

## Tác Giả

* Trần Văn Thiên Kim: BDD reachability
* Lê Đức Nguyên Khoa: Parser PNML và duyệt tường minh
* Nguyễn Trà My: Tối ưu hóa
* Nguyễn Hồng Phúc: Phát hiện deadlock
* Phan Phước Thiện Quang: BDD reachability

## API Reference 

### Class `PetriNet`

Class này chịu trách nhiệm phân tích file cấu trúc PNML, mô hình hóa mạng Petri dưới dạng ma trận và thực hiện tính toán các trạng thái khả đạt (reachable markings) bằng phương pháp duyệt đồ thị tường minh (Explicit State Space Exploration).

#### `__init__(self, pnml_file_path)`

**Chức năng:**

* Khởi tạo đối tượng mạng Petri.
* Thiết lập các cấu trúc dữ liệu rỗng (Places, Transitions, Ma trận liên thuộc).
* Tự động gọi phương thức `read_pnml_file` để nạp dữ liệu từ đường dẫn được cung cấp.

**Tham số:**

* `pnml_file_path`: Đường dẫn đến file `.pnml` chứa cấu trúc mạng Petri.

---

#### `read_pnml_file(self, file_path: str)`

Phân tích cú pháp file XML (định dạng PNML) để xây dựng mô hình toán học của mạng.

**Chức năng:**

* Sử dụng thư viện `xml.etree.ElementTree` để duyệt cây XML.
* Trích xuất danh sách **Places** và **Initial Marking** (trạng thái ban đầu).
* Trích xuất danh sách **Transitions**.
* Xây dựng hai ma trận trọng số cơ bản:
  * `self.pre_matrix`: Ma trận đầu vào (Place $\to$ Transition).
  * `self.post_matrix`: Ma trận đầu ra (Transition $\to$ Place).

**Tham số:**

* `file_path`: Đường dẫn tuyệt đối hoặc tương đối đến file `.pnml`.

---

#### `explicit_reachable_markings_computation(self, method="bfs")`

Thực hiện thuật toán duyệt đồ thị để tìm kiếm toàn bộ không gian trạng thái khả đạt từ trạng thái ban đầu ($M_0$).

**Chức năng:**

* Hỗ trợ hai chiến lược duyệt: **BFS** (Breadth-First Search) và **DFS** (Depth-First Search).
* Kiểm tra điều kiện kích hoạt (enable) của transition: $M \ge Pre$.
* Tính toán trạng thái mới theo công thức: $M_{new} = M - Pre + Post$.
* **Cơ chế Timeout:** Tự động dừng và trả về lỗi nếu thời gian thực thi vượt quá 10 giây.

**Tham số:**

* `method` (str): Phương pháp duyệt, chấp nhận `"bfs"` hoặc `"dfs"`. Mặc định là `"bfs"`.

**Trả về:** tuple gồm:

* `marking_states` (list): Danh sách các vector trạng thái (markings) tìm thấy. (Trả về `-1` nếu timeout).
* `elapsed_time` (float): Thời gian thực thi thuật toán tính bằng giây.

---

#### `print_reachable_markings(self, method="bfs")`

Hàm tiện ích dùng để thực thi thuật toán và in kết quả ra màn hình console theo định dạng dễ đọc.

**Chức năng:**

* Gọi hàm `explicit_reachable_markings_computation`.
* Hiển thị tổng số trạng thái và thời gian thực thi.
* Liệt kê chi tiết từng vector trạng thái tìm được.

**Đầu ra ví dụ:**

```text
Total states found: 5
Execution time: 0.001200 seconds
----------------------------------------
Reachable marking states
----------------------------------------
[1, 0, 0]
[0, 1, 0]
...

### Class `BDD_Reachability`

Class này cung cấp các phương thức để xây dựng và phân tích không gian trạng thái của mạng Petri sử dụng cấu trúc dữ liệu **Binary Decision Diagrams (BDD)**.

#### `__init__(self, petri_net: PetriNet)`

**Chức năng:**

* Khởi tạo đối tượng solver và thiết lập môi trường BDD.
* Tự động khai báo các cặp biến BDD cho mỗi Place:

  * `x_p`: Biến đại diện cho trạng thái hiện tại.
  * `y_p`: Biến đại diện cho trạng thái tiếp theo sau khi bắn transition.

**Tham số:**

* `petri_net`: Đối tượng chứa cấu trúc mạng Petri (Places, Transitions và các ma trận liên thuộc).

---

#### `build_transition(self)`

Xây dựng BDD khổng lồ đại diện cho **quan hệ chuyển đổi toàn cục** ( R_{total} ) của mạng.

**Chức năng:**

* Duyệt qua từng transition trong mạng.
* Tự động phát hiện Input arcs và Output arcs.
* Xây dựng logic **Enable** (điều kiện kích hoạt) và **Update** (cập nhật token).
* Áp dụng **Frame Axiom** cho các Place không tham gia transition (giữ nguyên giá trị token).

---

#### `compute_reachable_states(self)`

Thực hiện vòng lặp **fixed-point iteration** để tính toàn bộ tập trạng thái khả đạt từ trạng thái ban đầu.

**Trả về:** tuple gồm:

* `current_states` (BDD Object): Biểu diễn tập trạng thái.
* `total_states` (int): Số lượng trạng thái tìm thấy.
* `time` (float): Thời gian thực thi.

---

#### `print_reachable_states_list(self, states_bdd)`

Hàm tiện ích dùng để "giải nén" node BDD và in ra danh sách markings dạng dictionary.

**Đầu ra ví dụ:**

```
{'p1': 1, 'p2': 0, 'p3': 1}
```

---

#### `get_expr_from_bdd(self, bdd_node) -> str`

Trích xuất công thức logic từ một node BDD.

**Trả về:** Chuỗi ký tự dạng `ite(...)`.

**Mục đích:**

* Phân tích cấu trúc logic bên trong BDD.
* Hữu ích khi debug hoặc ghi log.

---

### `optimize_reachable_marking(self, reachable_bdd, weights=None)`

Tìm kiếm trạng thái tối ưu trong không gian trạng thái khả đạt dựa trên hệ thống trọng số tùy chỉnh.

**Chức năng:** 

* Duyệt qua các nghiệm (markings) chứa trong `reachable_bdd` bằng phương thức `pick_iter`.
* Tính toán điểm số (score) cho từng trạng thái theo công thức tổng quát: `score = Σ (has_token × weight)`.
* So sánh và lưu giữ trạng thái có **tổng điểm cao nhất**.

**Tham số:**

* `reachable_bdd`: Đối tượng BDD biểu diễn tập hợp các trạng thái khả đạt cần tìm kiếm.
* `weights` (dictionary, tùy chọn): Bảng trọng số cho từng Place (ví dụ: `{'p1': 10, 'p2': -5}`). Mặc định là 1 cho tất cả Places nếu để `None`

**Trả về:** tuple gồm:

* `best_marking` (dict): Cấu hình trạng thái đạt điểm cao nhất (hoặc None nếu không tìm thấy).
* `max_score` (float/int): Điểm số tối ưu tương ứng.
* `duration` (float): Thời gian thực thi quá trình tìm kiếm.

---

## License

Dự án được sử dụng cho mục đích học tập và nghiên cứu.

