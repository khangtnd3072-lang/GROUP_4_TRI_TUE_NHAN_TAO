# Backend

Backend dùng **Python + FastAPI** và kết nối **MySQL của XAMPP**.

## Thành phần chính

- `app/api/routes.py`: REST API cho môn học, Study Task, availability và schedule.
- `app/ai/priority.py`: Priority Scoring.
- `app/ai/constraints.py`: tạo Time Slot, repair và kiểm tra hard constraints.
- `app/ai/genetic_algorithm.py`: Genetic Algorithm.
- `app/ai/baseline.py`: Earliest Deadline First dùng làm baseline.
- `app/ai/scheduler.py`: điều phối toàn bộ quy trình sinh lịch.
- `app/db/database.py`: kết nối MySQL.
- `database/schema.sql`: tạo database/tables.
- `database/sample_data.sql`: dữ liệu demo.
- `tests/`: unit test phần AI.

## Quy tắc chính

- Slot cơ sở: 30 phút.
- Tối đa: 3 giờ học/ngày.
- Một phiên liên tục: tối đa 2 giờ.
- Khi đổi Task trong chuỗi slot liên tục phải có ít nhất 30 phút nghỉ.
- Không xếp sau deadline.
- Không phân bổ quá số giờ dự kiến của Task.
