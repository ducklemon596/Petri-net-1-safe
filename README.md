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

* Phát hiện trạng thái bế tắc bằng ILP kết hợp với BDD.

### **Task 5: Tối ưu hóa**

* Tìm marking khả đạt tối ưu dựa trên trọng số do người dùng định nghĩa hoặc đọc từ file.

## Cách Chạy

1. **Cài đặt thư viện phụ thuộc:**

   ```powershell
   pip install -r requirements.txt
   ```

2. **Chạy chương trình kiểm thử chính:**

   ```powershell
   python main.py
   ```

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

## License

Dự án được sử dụng cho mục đích học tập và nghiên cứu.

