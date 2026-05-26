# JSON-LD Linker – Open Data Knowledge Graph

**Đề tài #77 – Môn Cơ sở Dữ liệu Phân tán**  
**Nhóm:** GraphConnect  
**Thành viên:** Võ Văn Đạt  

---

## 1. Mô tả

Dự án mô phỏng một hệ thống cơ sở dữ liệu phân tán gồm 3 node lưu trữ dữ liệu nhà nghiên cứu theo từng lĩnh vực:

| Node    | Lĩnh vực                | Port  | File dữ liệu               |
|---------|-------------------------|-------|----------------------------|
| Node A  | CNTT / Computer Science | 5001  | `data/node_a_cntt.json`    |
| Node B  | Kinh tế / Economics     | 5002  | `data/node_b_kinh_te.json` |
| Node C  | Y tế / Medicine         | 5003  | `data/node_c_y_te.json`    |

Hệ thống sử dụng JSON-LD với các thẻ `@context` và `@id` để liên kết dữ liệu cục bộ với các snippets được lấy trực tiếp từ DBpedia thông qua SPARQL endpoint.

Master Node sẽ lấy dữ liệu từ 3 node, thực hiện thuật toán **Entity Disambiguation** để khử mơ hồ thực thể, sau đó cập nhật URI DBpedia phù hợp vào trường `@id`.

Mục tiêu chính:

- Mô phỏng phân mảnh ngang dữ liệu trên nhiều node.
- Liên kết dữ liệu local với các snippets thật được lấy từ DBpedia.
- Khử mơ hồ các nhà nghiên cứu trùng tên.
- Đánh giá Linkage Accuracy.
- Trực quan hóa kết quả bằng Knowledge Graph.
- Mô phỏng lỗi Node B trong hệ phân tán.

Trong phiên bản demo, dữ liệu local gồm 18 bản ghi. Trong đó có 16 bản ghi có DBpedia snippets tương ứng và 2 bản ghi không có DBpedia tương ứng để kiểm thử trường hợp không liên kết.
---

## 2. Cấu trúc thư mục

```text
jsonld-linker/
├── data/
│   ├── create_data.py
│   ├── create_dbpedia.py
│   ├── dbpedia_snippets.json
│   ├── node_a_cntt.json
│   ├── node_b_kinh_te.json
│   └── node_c_y_te.json
├── nodes/
│   ├── node_a.py
│   ├── node_b.py
│   └── node_c.py
├── link_algorithm.py
├── master.py
├── visualize.py
├── simulate_failure.py
├── knowledge_graph.png
└── README.md
```

---

## 3. Cài đặt

Cài các thư viện cần thiết:

```bash
python -m pip install flask requests networkx matplotlib
```

Nếu dùng môi trường ảo `venv`, có thể kích hoạt trước:

```bash
venv\Scripts\activate
```

---

## 4. Chuẩn bị dữ liệu

Trước khi chạy demo, nên tạo lại dữ liệu mẫu để các bản ghi local có `@id = null`:

```bash
python data/create_data.py
python data/create_dbpedia.py
```

Sau khi chạy, hệ thống sẽ tạo lại các file:

```text
data/node_a_cntt.json
data/node_b_kinh_te.json
data/node_c_y_te.json
data/dbpedia_snippets.json
```

---

## 5. Cách chạy hệ thống

Mở 4 terminal trong thư mục gốc project.

### Terminal 1 – Chạy Node A

```bash
python nodes/node_a.py
```

### Terminal 2 – Chạy Node B

```bash
python nodes/node_b.py
```

### Terminal 3 – Chạy Node C

```bash
python nodes/node_c.py
```

### Terminal 4 – Chạy Master

```bash
python master.py
```

Sau khi chạy `master.py`, hệ thống sẽ:

1. Đọc các snippets thật được lấy từ DBpedia.
2. Lấy dữ liệu từ 3 node.
3. Khử mơ hồ thực thể bằng thuật toán Entity Disambiguation.
4. Cập nhật URI DBpedia vào trường `@id`.
5. Tính Linkage Accuracy.
6. Vẽ Knowledge Graph và lưu thành file `knowledge_graph.png`.

---

## 6. Thuật toán Entity Disambiguation

Thuật toán nằm trong file:

```text
link_algorithm.py
```

Hệ thống tính điểm khớp giữa bản ghi local và bản ghi DBpedia theo 3 tiêu chí:

| Tiêu chí            | Trọng số  |
|---------------------|-----------|
| Tên nhà nghiên cứu  | 45 điểm   |
| Đơn vị công tác     | 25 điểm   |
| Lĩnh vực nghiên cứu | 30 điểm   |

Tổng điểm tối đa là 100.

Nếu điểm cao nhất lớn hơn hoặc bằng 50, hệ thống xem như liên kết thành công và cập nhật URI DBpedia vào trường `@id`.

Ví dụ local record:

```text
Alan Turing
University of Manchester
Computer Science
```
Hệ thống sẽ dựa vào `affiliation` và `researchArea` để chọn đúng URI tương ứng.

---

## 7. Kết quả mẫu

Khi chạy thành công, terminal sẽ hiển thị kết quả tương tự:

```text
Node A: 7/8 (87.5%)
Node B: 5/5 (100.0%)
Node C: 4/5 (80.0%)

Tổng Linkage Accuracy: 88.9%
```
Tập kiểm thử gồm 18 bản ghi local, trong đó 16 bản ghi có DBpedia snippets tương ứng và 2 bản ghi không có DBpedia tương ứng. Hai bản ghi không khớp sẽ được hệ thống đánh dấu là `unlinked` và giữ `@id = null`. Cách thiết kế này giúp kiểm tra cả trường hợp liên kết thành công và trường hợp không tìm được thực thể DBpedia phù hợp.

Do `master.py` xử lý các node song song bằng multi-threading nên log trên terminal có thể bị xen kẽ giữa các node. Kết quả tổng kết cuối cùng là kết quả chính xác.

---

## 8. Trực quan hóa Knowledge Graph

Sau khi chạy `master.py`, hệ thống sẽ tạo file:

```text
knowledge_graph.png
```

Trong đồ thị:

- Màu xanh: dữ liệu local đã liên kết thành công.
- Màu đỏ: dữ liệu DBpedia snippets.
- Đường nối: liên kết được tạo sau khi khử mơ hồ.
- Nhãn cạnh: điểm matching score.

Knowledge Graph chỉ hiển thị các liên kết được tạo thành công. Các bản ghi local không liên kết được với DBpedia sẽ không có cạnh nối trong graph, nhưng vẫn được tính vào Linkage Accuracy.

---

## 9. Demo giả lập lỗi Node B

Chạy:

```bash
python simulate_failure.py
```

Kịch bản demo:

1. Chương trình khởi động các node.
2. Node B bị ngắt để mô phỏng lỗi.
3. Master Node phát hiện Node B không phản hồi.
4. Hệ thống tiếp tục xử lý các node còn lại.
5. Kết quả vẫn được tổng hợp và vẽ graph.

Cơ chế này thể hiện khả năng **graceful degradation**: hệ thống không dừng hoàn toàn khi một node gặp lỗi.

---

## 10. Ghi chú về DBpedia snippets

File `dbpedia_snippets.json` không phải dữ liệu tự sinh thủ công. File này được tạo bằng script `data/create_dbpedia.py`. Script sẽ kết nối tới DBpedia SPARQL endpoint để lấy một số snippets thật từ DBpedia, sau đó chuẩn hóa về dạng JSON-LD để hệ thống xử lý ổn định.

Các URI trong trường `@id` là URI DBpedia thật, ví dụ:

```text
http://dbpedia.org/resource/Alan_Turing
http://dbpedia.org/resource/Adam_Smith
http://dbpedia.org/resource/Louis_Pasteur
```

Do dữ liệu DBpedia thật không phải lúc nào cũng có đầy đủ `affiliation` hoặc `field`, hệ thống có bước chuẩn hóa dữ liệu trước khi đưa vào thuật toán matching.

Trong demo hiện tại, hệ thống sử dụng 16 DBpedia snippets thật và 18 bản ghi local. Hai bản ghi local không có DBpedia tương ứng được dùng để kiểm thử khả năng từ chối liên kết khi điểm matching không đạt ngưỡng (<50).

---

## 11. Liên hệ lý thuyết

Dự án có liên hệ với các nội dung trong môn Cơ sở Dữ liệu Phân tán:

- **Horizontal Fragmentation:** chia dữ liệu theo lĩnh vực nghiên cứu.
- **Client/Server Architecture:** Master giao tiếp với các node qua REST API.
- **Distributed Processing:** Master xử lý song song bằng multi-threading.
- **Fault Tolerance:** hệ thống phát hiện node lỗi và tiếp tục xử lý node còn lại.
- **Semantic Data Management:** sử dụng JSON-LD, `@context`, `@id`.

---

## 12. Tác giả

**Nhóm:** GraphConnect  
**Thành viên:** Võ Văn Đạt  
**Môn học:** Cơ sở Dữ liệu Phân tán  
**Đề tài:** #77 – JSON-LD Linker: Open Data Knowledge Graph