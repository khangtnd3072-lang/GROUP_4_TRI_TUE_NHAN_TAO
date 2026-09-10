USE smart_study_scheduler;

-- File dữ liệu mẫu có thể import nhiều lần: dữ liệu cũ sẽ được xóa trước.
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE study_sessions;
TRUNCATE TABLE availability;
TRUNCATE TABLE study_tasks;
TRUNCATE TABLE subjects;
SET FOREIGN_KEY_CHECKS = 1;

INSERT INTO subjects(name, priority, difficulty) VALUES
('Trí tuệ nhân tạo', 5, 5),
('Lập trình Web', 4, 3),
('Cơ sở dữ liệu', 4, 4);

SET @ai_id = (SELECT id FROM subjects WHERE name = 'Trí tuệ nhân tạo' LIMIT 1);
SET @web_id = (SELECT id FROM subjects WHERE name = 'Lập trình Web' LIMIT 1);
SET @db_id = (SELECT id FROM subjects WHERE name = 'Cơ sở dữ liệu' LIMIT 1);

INSERT INTO study_tasks(subject_id, title, estimated_hours, deadline, priority, difficulty, notes, resource_link) VALUES
(@ai_id, 'Ôn Genetic Algorithm và làm demo', 4.0, TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 7 DAY), '23:59:00'), 5, 5, 'Tập trung biểu diễn chromosome và fitness function', 'https://en.wikipedia.org/wiki/Genetic_algorithm'),
(@web_id, 'Hoàn thiện giao diện bài tập lớn', 3.0, TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 9 DAY), '23:59:00'), 4, 3, 'Hoàn thiện dashboard và timeline', NULL),
(@db_id, 'Ôn truy vấn JOIN và chuẩn hóa', 2.5, TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 10 DAY), '23:59:00'), 3, 4, NULL, NULL);

INSERT INTO availability(study_date, start_time, end_time) VALUES
(DATE_ADD(CURDATE(), INTERVAL 1 DAY), '18:30:00', '22:00:00'),
(DATE_ADD(CURDATE(), INTERVAL 2 DAY), '19:00:00', '22:00:00'),
(DATE_ADD(CURDATE(), INTERVAL 3 DAY), '08:00:00', '11:30:00'),
(DATE_ADD(CURDATE(), INTERVAL 4 DAY), '19:00:00', '22:00:00'),
(DATE_ADD(CURDATE(), INTERVAL 5 DAY), '18:30:00', '22:00:00'),
(DATE_ADD(CURDATE(), INTERVAL 6 DAY), '19:00:00', '22:00:00'),
(DATE_ADD(CURDATE(), INTERVAL 7 DAY), '19:00:00', '22:00:00'),
(DATE_ADD(CURDATE(), INTERVAL 8 DAY), '19:00:00', '22:00:00'),
(DATE_ADD(CURDATE(), INTERVAL 9 DAY), '19:00:00', '22:00:00');
