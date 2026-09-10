# HƯỚNG DẪN CHẠY CHƯƠNG TRÌNH CHI TIẾT

## 1. Tổng quan

Dự án gồm hai phần tách biệt:

- `FE/`: Frontend dùng **HTML + CSS + JavaScript thuần**.
- `BE/`: Backend dùng **Python FastAPI**, kết nối **MySQL chạy trong XAMPP**.

Ứng dụng không có đăng ký/đăng nhập. Đây là phiên bản demo cho một người dùng.

Các cổng mặc định:

- Frontend: `http://127.0.0.1:5500`
- Backend: `http://127.0.0.1:8000`
- Swagger API: `http://127.0.0.1:8000/docs`
- MySQL XAMPP: `127.0.0.1:3306`

---

## 2. Phần mềm cần cài trước

Trên Windows cần có:

1. **Python 3.11 trở lên**
2. **XAMPP** có MySQL/MariaDB và phpMyAdmin
3. Trình duyệt Chrome, Edge hoặc Firefox

Không cần cài Node.js, npm, React hay bất kỳ framework Frontend nào.

Kiểm tra Python bằng CMD hoặc PowerShell:

```bat
python --version
```

hoặc:

```bat
py --version
```

Nếu hiện phiên bản Python thì có thể tiếp tục.

---

## 3. Cấu trúc thư mục

```text
ai-study-scheduler/
├── FE/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── api.js
│   │   └── app.js
│   └── run_frontend.bat
│
├── BE/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   └── routes.py
│   │   ├── ai/
│   │   │   ├── priority.py
│   │   │   ├── constraints.py
│   │   │   ├── genetic_algorithm.py
│   │   │   ├── baseline.py
│   │   │   ├── scheduler.py
│   │   │   └── models.py
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── db/
│   │   │   └── database.py
│   │   └── schemas/
│   │       └── requests.py
│   ├── database/
│   │   ├── schema.sql
│   │   └── sample_data.sql
│   ├── tests/
│   ├── experiments/
│   ├── requirements.txt
│   ├── .env.example
│   ├── setup_backend.bat
│   └── run_backend.bat
│
├── docs/
├── README.md
├── HUONG_DAN_CHAY_CHUONG_TRINH.md
└── run_all.bat
```

---

# 4. Bước 1 — Khởi động MySQL trong XAMPP

1. Mở **XAMPP Control Panel**.
2. Tìm dòng **MySQL**.
3. Bấm **Start**.
4. Khi MySQL chuyển sang trạng thái đang chạy thì tiếp tục.

> Không bắt buộc bật Apache để chạy ứng dụng. Apache chỉ cần nếu bạn muốn dùng phpMyAdmin thông qua XAMPP theo cách thông thường.

Để mở phpMyAdmin:

1. Có thể Start cả **Apache**.
2. Trên XAMPP bấm **Admin** ở dòng MySQL, hoặc mở:

```text
http://localhost/phpmyadmin
```

---

# 5. Bước 2 — Tạo database

Trong phpMyAdmin:

1. Chọn tab **Import**.
2. Chọn file:

```text
BE/database/schema.sql
```

3. Bấm **Import/Go**.

File này tạo database:

```text
smart_study_scheduler
```

và các bảng:

- `subjects`
- `study_tasks`
- `availability`
- `study_sessions`

## Dữ liệu mẫu

Nếu muốn demo ngay, import thêm:

```text
BE/database/sample_data.sql
```

File này tạo sẵn:

- môn Trí tuệ nhân tạo;
- môn Lập trình Web;
- môn Cơ sở dữ liệu;
- một số Study Task;
- nhiều khoảng thời gian rảnh.

**Lưu ý:** `sample_data.sql` sẽ xóa dữ liệu demo cũ trong 4 bảng trước khi tạo lại dữ liệu mẫu.

---

# 6. Bước 3 — Cài Backend Python

Mở CMD tại thư mục dự án rồi chạy:

```bat
cd BE
```

Tạo virtual environment:

```bat
py -m venv .venv
```

Nếu máy không nhận lệnh `py`, dùng:

```bat
python -m venv .venv
```

Kích hoạt môi trường:

```bat
.venv\Scripts\activate
```

Cài thư viện:

```bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Hoặc có thể chạy trực tiếp:

```text
BE/setup_backend.bat
```

Script này tự tạo `.venv`, cài dependency và tạo file `.env` mặc định.

---

# 7. Bước 4 — Cấu hình kết nối XAMPP

Trong thư mục `BE`, sao chép:

```text
.env.example
```

thành:

```text
.env
```

Cấu hình mặc định:

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=smart_study_scheduler

FRONTEND_ORIGINS=http://localhost:5500,http://127.0.0.1:5500

SLOT_MINUTES=30
MAX_STUDY_HOURS_PER_DAY=3
MAX_SESSION_HOURS=2
```

Với XAMPP mặc định, tài khoản MySQL thường là:

```text
user: root
password: để trống
port: 3306
```

Nếu máy bạn đã đổi mật khẩu hoặc cổng MySQL, sửa `.env` tương ứng.

Ví dụ nếu MySQL chạy cổng 3307:

```env
DB_PORT=3307
```

---

# 8. Bước 5 — Chạy Backend

Cách nhanh nhất: double-click

```text
BE/run_backend.bat
```

Hoặc chạy bằng CMD:

```bat
cd BE
.venv\Scripts\activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Khi chạy thành công sẽ thấy thông báo tương tự:

```text
Uvicorn running on http://127.0.0.1:8000
```

Kiểm tra Backend:

```text
http://127.0.0.1:8000/health
```

Kết quả mong đợi:

```json
{
  "status": "ok",
  "service": "AI Study Scheduler API"
}
```

Có thể xem và thử API tại:

```text
http://127.0.0.1:8000/docs
```

---

# 9. Bước 6 — Chạy Frontend

Không nên double-click trực tiếp `index.html` vì JavaScript Module và CORS hoạt động ổn định hơn khi chạy qua HTTP server.

Cách nhanh nhất: double-click

```text
FE/run_frontend.bat
```

Hoặc mở một CMD mới:

```bat
cd FE
py -m http.server 5500 --bind 127.0.0.1
```

Nếu máy không có `py`:

```bat
python -m http.server 5500 --bind 127.0.0.1
```

Sau đó mở:

```text
http://127.0.0.1:5500
```

---

# 10. Chạy cả Frontend và Backend bằng một lệnh

Sau khi đã cài Backend và tạo database, có thể double-click:

```text
run_all.bat
```

Script sẽ mở hai cửa sổ CMD:

1. Backend ở cổng `8000`.
2. Frontend ở cổng `5500`.

Sau đó mở trình duyệt tại:

```text
http://127.0.0.1:5500
```

---

# 11. Luồng sử dụng chương trình

## Bước 1 — Thêm môn học

Nhập:

- tên môn;
- mức ưu tiên 1–5;
- độ khó 1–5.

## Bước 2 — Nhập thời gian rảnh

Chọn:

- ngày;
- giờ bắt đầu;
- giờ kết thúc.

AI chỉ được lập lịch trong những khoảng này.

## Bước 3 — Thêm Study Task

Nhập:

- môn học;
- tên công việc;
- số giờ dự kiến;
- deadline;
- priority;
- difficulty;
- ghi chú;
- link tài liệu nếu có.

## Bước 4 — Sinh lịch AI

Bấm:

```text
Tạo lịch học bằng AI
```

Backend sẽ thực hiện:

```text
Priority Scoring
      ↓
Constraint Satisfaction
      ↓
Genetic Algorithm
      ↓
Fitness Function
      ↓
Best Schedule
```

Sau đó Frontend hiển thị:

- Fitness của Genetic Algorithm;
- Fitness của EDF Baseline;
- số thế hệ đã chạy;
- số giờ được phân bổ;
- Priority Score của từng Task;
- Timeline học tập.

## Bước 5 — Theo dõi tiến độ

Trong Timeline có thể:

- mở rộng card;
- xem notes;
- mở link tài liệu;
- đánh dấu hoàn thành;
- đánh dấu bỏ lỡ.

Nếu bỏ lỡ một phiên, bấm lại **Tạo lịch học bằng AI**. Hệ thống giữ các phiên đã hoàn thành và chỉ lập lại phần thời lượng còn thiếu của Task.

---

# 12. Quy tắc lập lịch của bài tập lớn

Phiên bản hiện tại áp dụng:

1. Mỗi Time Slot cơ sở = **30 phút**.
2. Tổng thời gian học tối đa = **3 giờ/ngày**.
3. Một phiên học liên tục tối đa = **2 giờ**.
4. Mỗi phiên tối thiểu thực tế = **1 slot = 30 phút**.
5. Khi chuyển sang Task khác trong một chuỗi thời gian liên tục, hệ thống tạo ít nhất **30 phút nghỉ**.
6. Không lập lịch ngoài thời gian rảnh.
7. Không xếp Task sau deadline.
8. Không phân bổ nhiều hơn thời lượng Task cần.
9. Task gần deadline, priority cao, difficulty cao và workload lớn nhận Priority Score cao hơn.

Priority Score:

```text
0.45 × Deadline Urgency
+ 0.30 × Priority
+ 0.15 × Difficulty
+ 0.10 × Workload
```

---

# 13. Chạy Unit Test phần AI

Mở CMD:

```bat
cd BE
.venv\Scripts\activate
pytest -q
```

Các test tập trung vào:

- Priority Scoring;
- slot 30 phút;
- giới hạn 3 giờ/ngày;
- deadline;
- giới hạn thời lượng phiên;
- Genetic Algorithm trả về lịch hợp lệ.

---

# 14. Chạy thực nghiệm Genetic Algorithm và EDF

Trong thư mục `BE`:

```bat
.venv\Scripts\activate
python experiments\run_experiments.py
```

Kết quả được lưu vào:

```text
BE/experiments/results.csv
```

Dùng kết quả thật này cho phần thực nghiệm của báo cáo. Không nên tự tạo số liệu.

---

# 15. Các lỗi thường gặp

## Lỗi: `ModuleNotFoundError`

Nguyên nhân thường là chưa kích hoạt `.venv` hoặc chưa cài requirements.

Chạy lại:

```bat
cd BE
.venv\Scripts\activate
pip install -r requirements.txt
```

## Lỗi: `Can't connect to MySQL server`

Kiểm tra:

- MySQL trong XAMPP đã Start chưa.
- `DB_PORT` có đúng không.
- database `smart_study_scheduler` đã được import chưa.

## Lỗi: `Access denied for user 'root'`

MySQL của máy có mật khẩu. Sửa:

```env
DB_PASSWORD=mat_khau_cua_ban
```

trong `BE/.env`.

## Lỗi Frontend báo không kết nối được Backend

Kiểm tra Backend có đang chạy ở:

```text
http://127.0.0.1:8000/health
```

Nếu không mở được, chạy lại Backend trước.

## Lỗi CORS

Frontend mặc định phải chạy ở:

```text
http://127.0.0.1:5500
```

Nếu bạn đổi cổng Frontend, cần thêm origin mới vào:

```env
FRONTEND_ORIGINS=...
```

sau đó restart Backend.

## Lỗi `422 Unprocessable Entity` khi thêm Task

Kiểm tra:

- deadline phải hợp lệ;
- estimated hours tối thiểu 0.5;
- priority/difficulty từ 1 đến 5;
- URL tài liệu phải là URL hợp lệ nếu có nhập.

## AI báo không thể tạo lịch hợp lệ

Kiểm tra:

- đã có Task chưa;
- đã nhập availability chưa;
- availability phải nằm trước deadline;
- có đủ thời gian rảnh hay không.

Hệ thống vẫn giới hạn 3 giờ/ngày nên nếu tổng công việc quá lớn thì có thể chỉ lập được một phần.

---

# 16. Tắt chương trình

Tại hai cửa sổ CMD của Frontend và Backend, nhấn:

```text
Ctrl + C
```

Sau đó có thể Stop MySQL trong XAMPP.
