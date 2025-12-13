# Student Management REST API

A comprehensive REST API for managing student records with full CRUD operations, JWT authentication, search functionality, and support for both JSON and XML output formats.

## Table of Contents
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Database Schema](#database-schema)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Security](#security)
- [Project Structure](#project-structure)

## Features

✅ **CRUD Operations**: Complete Create, Read, Update, Delete functionality  
✅ **JWT Authentication**: Secure API endpoints with JSON Web Tokens  
✅ **Input Validation**: Comprehensive validation and error handling  
✅ **Search Functionality**: Search students by name, email, grade level, or age  
✅ **Multiple Formats**: Support for both JSON and XML output  
✅ **Comprehensive Testing**: Unit tests covering all endpoints and edge cases  
✅ **RESTful Design**: Follows REST API best practices  
✅ **Error Handling**: Proper HTTP status codes and error messages  

## Technologies Used

- **Flask**: Web framework for Python
- **MySQL**: Database management system
- **Flask-JWT-Extended**: JWT authentication
- **mysql-connector-python**: MySQL database connector
- **dicttoxml**: XML conversion library
- **unittest**: Testing framework

## Database Schema

### Students Table
```sql
CREATE TABLE students (
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
```

## Installation

### Prerequisites
- Python 3.8 or higher
- MySQL Server 8.0 or higher
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/student-management-api.git
cd student-management-api
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Up MySQL Database
```bash
# Login to MySQL
mysql -u root -p

# Run the database schema
source database_schema.sql

# Or import manually
mysql -u root -p < database_schema.sql
```

## Configuration

### Database Configuration
Edit the `DB_CONFIG` in `app.py`:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',  # Change this
    'database': 'student_management'
}
```

### JWT Configuration
Change the JWT secret key in `app.py`:

```python
app.config['JWT_SECRET_KEY'] = 'your-secret-key-here'
```

## Running the Application

### Start the Flask Server
```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Check API Health
```bash
curl http://localhost:5000/api/health
```

## API Documentation

### Base URL
```
http://localhost:5000/api
```

### Authentication

#### Login
Get JWT access token for API access.

**Endpoint:** `POST /api/auth/login`

**Request Body:**
```json
{
    "username": "admin",
    "password": "admin123"
}
```

**Response (200 OK):**
```json
{
    "success": true,
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "message": "Login successful"
}
```

**Note:** Use the access token in the Authorization header for all protected endpoints:
```
Authorization: Bearer <access_token>
```

---

### Student Operations

#### 1. Create Student
Create a new student record.

**Endpoint:** `POST /api/students`  
**Authentication:** Required  

**Request Body:**
```json
{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@school.edu",
    "age": 16,
    "grade_level": 10,
    "phone": "555-0101",
    "address": "123 Main St"
}
```

**Response (201 Created):**
```json
{
    "success": true,
    "message": "Student created successfully",
    "student_id": 26
}
```

**Validation Rules:**
- `first_name`: Required, max 50 characters
- `last_name`: Required, max 50 characters
- `email`: Required, valid email format, unique
- `age`: Required, integer between 5 and 100
- `grade_level`: Required, integer between 1 and 12
- `phone`: Optional, max 20 characters
- `address`: Optional

#### 2. Get All Students
Retrieve all students or search with filters.

**Endpoint:** `GET /api/students`  
**Authentication:** Required  

**Query Parameters:**
- `name`: Search by first or last name
- `email`: Search by email
- `grade_level`: Filter by grade level
- `age`: Filter by age
- `format`: Output format (json or xml)

**Example:**
```bash
GET /api/students?name=John&format=json
GET /api/students?grade_level=10
```

**Response (200 OK):**
```json
{
    "success": true,
    "count": 25,
    "students": [
        {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@school.edu",
            "age": 16,
            "grade_level": 10,
            "phone": "555-0101",
            "address": "123 Main St",
            "created_at": "2024-12-13 10:30:00",
            "updated_at": "2024-12-13 10:30:00"
        }
    ]
}
```

#### 3. Get Student by ID
Retrieve a specific student by ID.

**Endpoint:** `GET /api/students/{student_id}`  
**Authentication:** Required  

**Example:**
```bash
GET /api/students/1
```

**Response (200 OK):**
```json
{
    "success": true,
    "student": {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@school.edu",
        "age": 16,
        "grade_level": 10,
        "phone": "555-0101",
        "address": "123 Main St",
        "created_at": "2024-12-13 10:30:00",
        "updated_at": "2024-12-13 10:30:00"
    }
}
```

**Response (404 Not Found):**
```json
{
    "success": false,
    "error": "Student not found"
}
```

#### 4. Update Student
Update an existing student record.

**Endpoint:** `PUT /api/students/{student_id}`  
**Authentication:** Required  

**Request Body (partial update allowed):**
```json
{
    "first_name": "Jane",
    "age": 17,
    "grade_level": 11
}
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Student updated successfully"
}
```

#### 5. Delete Student
Delete a student record.

**Endpoint:** `DELETE /api/students/{student_id}`  
**Authentication:** Required  

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Student deleted successfully"
}
```

---

### Format Options

All GET endpoints support XML and JSON formats using the `format` query parameter.

**JSON Format (default):**
```bash
GET /api/students?format=json
```

**XML Format:**
```bash
GET /api/students?format=xml
```

**XML Response Example:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<response>
    <success>true</success>
    <count>25</count>
    <students>
        <item>
            <id>1</id>
            <first_name>John</first_name>
            <last_name>Doe</last_name>
            <email>john.doe@school.edu</email>
            <age>16</age>
            <grade_level>10</grade_level>
        </item>
    </students>
</response>
```

---

### HTTP Status Codes

- `200 OK`: Request succeeded
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid input or validation error
- `401 Unauthorized`: Missing or invalid authentication
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource already exists (duplicate email)
- `500 Internal Server Error`: Server error

---

## Testing

### Run All Tests
```bash
python test_api.py
```

### Run Specific Test
```bash
python -m unittest test_api.StudentAPITestCase.test_01_login_success
```

### Test Coverage
The test suite includes:
- ✅ Authentication tests (login success/failure)
- ✅ CRUD operation tests
- ✅ Input validation tests
- ✅ Error handling tests
- ✅ Search functionality tests
- ✅ Format conversion tests (JSON/XML)
- ✅ Edge cases and boundary tests

---

## Security

### JWT Authentication
- All student endpoints require JWT authentication
- Tokens expire after 1 hour
- Include token in Authorization header: `Bearer <token>`

### Input Validation
- Email format validation
- Age range validation (5-100)
- Grade level validation (1-12)
- SQL injection prevention using parameterized queries
- Unique email constraint

### Best Practices
- Change default credentials in production
- Use environment variables for sensitive data
- Enable HTTPS in production
- Implement rate limiting
- Add logging for security events

---

## Project Structure

```
student-management-api/
│
├── app.py                  # Main Flask application
├── test_api.py            # Unit tests
├── database_schema.sql    # Database schema and sample data
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
├── README.md             # This file
│
└── venv/                 # Virtual environment (not in git)
```

---

## Usage Examples

### Using cURL

**1. Login:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**2. Create Student:**
```bash
curl -X POST http://localhost:5000/api/students \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "first_name": "Alice",
    "last_name": "Johnson",
    "email": "alice.johnson@school.edu",
    "age": 17,
    "grade_level": 11,
    "phone": "555-0199",
    "address": "456 Oak Avenue"
  }'
```

**3. Get All Students:**
```bash
curl -X GET "http://localhost:5000/api/students" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**4. Search Students:**
```bash
curl -X GET "http://localhost:5000/api/students?name=Alice&format=json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**5. Update Student:**
```bash
curl -X PUT http://localhost:5000/api/students/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"grade_level": 12, "age": 18}'
```

**6. Delete Student:**
```bash
curl -X DELETE http://localhost:5000/api/students/1 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:5000/api"

# Login
login_response = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
token = login_response.json()['access_token']

# Set headers
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Create student
new_student = {
    "first_name": "Bob",
    "last_name": "Smith",
    "email": "bob.smith@school.edu",
    "age": 16,
    "grade_level": 10
}
response = requests.post(f"{BASE_URL}/students", json=new_student, headers=headers)
print(response.json())

# Get all students
response = requests.get(f"{BASE_URL}/students", headers=headers)
print(response.json())
```

---

## Common Issues and Solutions

### Issue: "Access denied for user"
**Solution:** Check MySQL username and password in `app.py`

### Issue: "Database does not exist"
**Solution:** Run `database_schema.sql` to create the database

### Issue: "401 Unauthorized"
**Solution:** Ensure you're including the JWT token in the Authorization header

### Issue: "Module not found"
**Solution:** Activate virtual environment and install requirements:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is for educational purposes as part of the CSE1 Final Project.

---

## Contact

For questions or support, please contact the project maintainer.

---
