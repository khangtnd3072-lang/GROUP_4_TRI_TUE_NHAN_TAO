# Hệ thống lập lịch học thông minh sử dụng Trí tuệ nhân tạo

Bài tập lớn môn **Trí tuệ nhân tạo**. Hệ thống nhận môn học, Study Task, deadline, độ khó, mức ưu tiên và thời gian rảnh, sau đó sử dụng **Priority Scoring + Constraint Satisfaction + Genetic Algorithm** để tạo lịch học.

## Công nghệ đã chốt

- **FE:** HTML + CSS + JavaScript thuần.
- **BE:** Python + FastAPI.
- **Database:** MySQL chạy bằng XAMPP.
- **Tài khoản:** không đăng ký, không đăng nhập; demo một người dùng.
- **AI:** Priority Scoring, Constraint Satisfaction, Genetic Algorithm, Fitness Function.
- **Baseline:** Earliest Deadline First.
- **Giới hạn học:** tối đa **3 giờ/ngày**.
- **Phiên học:** 30 phút đến tối đa 2 giờ; có khoảng nghỉ khi đổi Task trong chuỗi thời gian liên tục.

## Cấu trúc

```text
ai-study-scheduler/
├── FE/                       # HTML/CSS/JS
│   ├── index.html
│   ├── css/style.css
│   ├── js/api.js
│   ├── js/app.js
│   └── run_frontend.bat
│
├── BE/                       # Python FastAPI + AI + MySQL
│   ├── app/
│   │   ├── api/
│   │   ├── ai/
│   │   ├── core/
│   │   ├── db/
│   │   └── schemas/
│   ├── database/
│   │   ├── schema.sql
│   │   └── sample_data.sql
│   ├── tests/
│   ├── experiments/
│   ├── requirements.txt
│   ├── setup_backend.bat
│   └── run_backend.bat
│
├── docs/
├── HUONG_DAN_CHAY_CHUONG_TRINH.md
└── run_all.bat
```

## Luồng AI

```text
Study Task + Availability
          ↓
    Priority Scoring
          ↓
 Constraint Satisfaction
          ↓
    Genetic Algorithm
          ↓
    Fitness Function
          ↓
      Best Schedule
          ↓
       Timeline
```

Priority Score hiện dùng:

```text
0.45 × deadline_urgency
+ 0.30 × priority
+ 0.15 × difficulty
+ 0.10 × workload
```

## Chạy nhanh

1. Start **MySQL** trong XAMPP.
2. Import `BE/database/schema.sql` bằng phpMyAdmin.
3. Có thể import `BE/database/sample_data.sql` để có dữ liệu demo.
4. Chạy `BE/setup_backend.bat` một lần.
5. Chạy `run_all.bat`.
6. Mở `http://127.0.0.1:5500`.

Hướng dẫn đầy đủ, xử lý lỗi và lệnh kiểm thử nằm trong:

**`HUONG_DAN_CHAY_CHUONG_TRINH.md`**
