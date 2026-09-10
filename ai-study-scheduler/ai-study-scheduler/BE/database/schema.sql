CREATE DATABASE IF NOT EXISTS smart_study_scheduler
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE smart_study_scheduler;

CREATE TABLE IF NOT EXISTS subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    priority TINYINT NOT NULL DEFAULT 3,
    difficulty TINYINT NOT NULL DEFAULT 3,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_subject_priority CHECK (priority BETWEEN 1 AND 5),
    CONSTRAINT chk_subject_difficulty CHECK (difficulty BETWEEN 1 AND 5)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS study_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL,
    title VARCHAR(180) NOT NULL,
    estimated_hours DECIMAL(5,2) NOT NULL,
    deadline DATETIME NOT NULL,
    priority TINYINT NOT NULL DEFAULT 3,
    difficulty TINYINT NOT NULL DEFAULT 3,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    notes TEXT NULL,
    resource_link VARCHAR(500) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_task_subject FOREIGN KEY (subject_id) REFERENCES subjects(id),
    CONSTRAINT chk_task_hours CHECK (estimated_hours > 0),
    CONSTRAINT chk_task_priority CHECK (priority BETWEEN 1 AND 5),
    CONSTRAINT chk_task_difficulty CHECK (difficulty BETWEEN 1 AND 5),
    CONSTRAINT chk_task_status CHECK (status IN ('pending', 'in_progress', 'completed'))
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS availability (
    id INT AUTO_INCREMENT PRIMARY KEY,
    study_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_availability_time CHECK (end_time > start_time)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS study_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL,
    session_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    duration_hours DECIMAL(5,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'planned',
    fitness_score DECIMAL(10,4) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_session_task FOREIGN KEY (task_id) REFERENCES study_tasks(id) ON DELETE CASCADE,
    CONSTRAINT chk_session_time CHECK (end_time > start_time),
    CONSTRAINT chk_session_duration CHECK (duration_hours > 0),
    CONSTRAINT chk_session_status CHECK (status IN ('planned', 'completed', 'missed'))
) ENGINE=InnoDB;

CREATE INDEX idx_task_deadline ON study_tasks(deadline);
CREATE INDEX idx_availability_date ON availability(study_date);
CREATE INDEX idx_session_date ON study_sessions(session_date);
