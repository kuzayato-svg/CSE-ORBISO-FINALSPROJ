-- database_schema.sql
CREATE DATABASE IF NOT EXISTS student_management;
USE student_management;

CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    age INT NOT NULL,
    grade_level INT NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Sample data (optional)
INSERT INTO students (first_name, last_name, email, age, grade_level, phone, address) VALUES
('John', 'Doe', 'john.doe@school.edu', 16, 10, '555-0101', '123 Main St'),
('Jane', 'Smith', 'jane.smith@school.edu', 17, 11, '555-0102', '456 Oak Ave');