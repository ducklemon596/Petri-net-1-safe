# Dự án Phân Tích Mạng Petri

Dự án này cung cấp một khung làm việc mô-đun để phân tích các mạng Petri 1-safe bằng nhiều kỹ thuật khác nhau. Toàn bộ được chia thành nhiều tác vụ, mỗi tác vụ được triển khai trong một mô-đun riêng nhằm đảm bảo rõ ràng và dễ mở rộng.

## Cấu Trúc Dự Án

```
requirements.txt
Task1_Parser/
    task1.py           # Bộ phân tích PetriNet (PNML, trọng số)
Task2_Explicit/
    task2.py           # Duyệt không gian trạng thái theo phương pháp tường minh
Task3_BDD/
    task3.py           # Phân tích trạng thái có thể đạt được sử dụng BDD
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

### **Task 3: Symbolic computation bằng BDD**

* Sử dụng Binary Decision Diagrams (BDD) để biểu diễn và phân tích hiệu quả các trạng thái khả đạt.

### **Task 4: Phát hiện Deadlock**

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

## License

Dự án được sử dụng cho mục đích giáo dục và nghiên cứu.
