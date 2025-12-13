import logging
logging.basicConfig(level=logging.INFO)
from flask import Flask, request, jsonify, make_response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import mysql.connector
from mysql.connector import Error
import dicttoxml
from functools import wraps
from datetime import timedelta
import os

app = Flask(__name__)

# Configuration
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

jwt = JWTManager(app)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',  # Change this to your MySQL password
    'database': 'student_management'
}

# Helper function to get database connection
def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Helper function to format response
def format_response(data, status_code=200):
    """Format response as JSON or XML based on format parameter"""
    output_format = request.args.get('format', 'json').lower()
    
    if output_format == 'xml':
        xml_data = dicttoxml.dicttoxml(data, custom_root='response', attr_type=False)
        response = make_response(xml_data)
        response.headers['Content-Type'] = 'application/xml'
        response.status_code = status_code
        return response
    else:
        response = jsonify(data)
        response.status_code = status_code
        return response

# Error handler for validation
def validate_student_data(data, required_fields=None):
    """Validate student data"""
    if required_fields is None:
        required_fields = ['first_name', 'last_name', 'email', 'age', 'grade_level']
    
    errors = []
    
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"{field} is required")
    
    if 'email' in data and data['email']:
        if '@' not in data['email'] or '.' not in data['email']:
            errors.append("Invalid email format")
    
    if 'age' in data and data['age']:
        try:
            age = int(data['age'])
            if age < 5 or age > 100:
                errors.append("Age must be between 5 and 100")
        except ValueError:
            errors.append("Age must be a number")
    
    if 'grade_level' in data and data['grade_level']:
        try:
            grade = int(data['grade_level'])
            if grade < 1 or grade > 12:
                errors.append("Grade level must be between 1 and 12")
        except ValueError:
            errors.append("Grade level must be a number")
    
    return errors

# Authentication endpoint
@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login endpoint to get JWT token"""
    try:
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data:
            return format_response({
                'success': False,
                'error': 'Username and password are required'
            }, 400)
        
        # Simple authentication (in production, verify against database with hashed passwords)
        if data['username'] == 'admin' and data['password'] == 'admin123':
            access_token = create_access_token(identity=data['username'])
            return format_response({
                'success': True,
                'access_token': access_token,
                'message': 'Login successful'
            }, 200)
        else:
            return format_response({
                'success': False,
                'error': 'Invalid credentials'
            }, 401)
    
    except Exception as e:
        return format_response({
            'success': False,
            'error': str(e)
        }, 500)

# CREATE - Add a new student
@app.route('/api/students', methods=['POST'])
@jwt_required()
def create_student():
    """Create a new student record"""
    try:
        data = request.get_json()
        
        # Validate input
        errors = validate_student_data(data)
        if errors:
            return format_response({
                'success': False,
                'errors': errors
            }, 400)
        
        connection = get_db_connection()
        if not connection:
            return format_response({
                'success': False,
                'error': 'Database connection failed'
            }, 500)
        
        cursor = connection.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT id FROM students WHERE email = %s", (data['email'],))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return format_response({
                'success': False,
                'error': 'Email already exists'
            }, 409)
        
        # Insert new student
        query = """
            INSERT INTO students (first_name, last_name, email, age, grade_level, phone, address)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            data['first_name'],
            data['last_name'],
            data['email'],
            data['age'],
            data['grade_level'],
            data.get('phone', ''),
            data.get('address', '')
        )
        
        cursor.execute(query, values)
        connection.commit()
        student_id = cursor.lastrowid
        
        cursor.close()
        connection.close()
        
        return format_response({
            'success': True,
            'message': 'Student created successfully',
            'student_id': student_id
        }, 201)
    
    except Error as e:
        return format_response({
            'success': False,
            'error': f'Database error: {str(e)}'
        }, 500)
    except Exception as e:
        return format_response({
            'success': False,
            'error': str(e)
        }, 500)

# READ - Get all students or search
@app.route('/api/students', methods=['GET'])
@jwt_required()
def get_students():
    """Get all students or search with filters"""
    try:
        connection = get_db_connection()
        if not connection:
            return format_response({
                'success': False,
                'error': 'Database connection failed'
            }, 500)
        
        cursor = connection.cursor(dictionary=True)
        
        # Search parameters
        search_name = request.args.get('name', '')
        search_email = request.args.get('email', '')
        search_grade = request.args.get('grade_level', '')
        search_age = request.args.get('age', '')
        
        # Build query with search filters
        query = "SELECT * FROM students WHERE 1=1"
        params = []
        
        if search_name:
            query += " AND (first_name LIKE %s OR last_name LIKE %s)"
            params.extend([f"%{search_name}%", f"%{search_name}%"])
        
        if search_email:
            query += " AND email LIKE %s"
            params.append(f"%{search_email}%")
        
        if search_grade:
            query += " AND grade_level = %s"
            params.append(search_grade)
        
        if search_age:
            query += " AND age = %s"
            params.append(search_age)
        
        query += " ORDER BY id"
        
        cursor.execute(query, params)
        students = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return format_response({
            'success': True,
            'count': len(students),
            'students': students
        }, 200)
    
    except Error as e:
        return format_response({
            'success': False,
            'error': f'Database error: {str(e)}'
        }, 500)
    except Exception as e:
        return format_response({
            'success': False,
            'error': str(e)
        }, 500)

# READ - Get single student by ID
@app.route('/api/students/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student(student_id):
    """Get a single student by ID"""
    try:
        connection = get_db_connection()
        if not connection:
            return format_response({
                'success': False,
                'error': 'Database connection failed'
            }, 500)
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        student = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if student:
            return format_response({
                'success': True,
                'student': student
            }, 200)
        else:
            return format_response({
                'success': False,
                'error': 'Student not found'
            }, 404)
    
    except Error as e:
        return format_response({
            'success': False,
            'error': f'Database error: {str(e)}'
        }, 500)
    except Exception as e:
        return format_response({
            'success': False,
            'error': str(e)
        }, 500)

# UPDATE - Update student information
@app.route('/api/students/<int:student_id>', methods=['PUT'])
@jwt_required()
def update_student(student_id):
    """Update a student record"""
    try:
        data = request.get_json()
        
        if not data:
            return format_response({
                'success': False,
                'error': 'No data provided'
            }, 400)
        
        # Validate input (only fields that are provided)
        errors = validate_student_data(data, required_fields=[])
        if errors:
            return format_response({
                'success': False,
                'errors': errors
            }, 400)
        
        connection = get_db_connection()
        if not connection:
            return format_response({
                'success': False,
                'error': 'Database connection failed'
            }, 500)
        
        cursor = connection.cursor()
        
        # Check if student exists
        cursor.execute("SELECT id FROM students WHERE id = %s", (student_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            return format_response({
                'success': False,
                'error': 'Student not found'
            }, 404)
        
        # Check if new email already exists (if email is being updated)
        if 'email' in data:
            cursor.execute("SELECT id FROM students WHERE email = %s AND id != %s", 
                          (data['email'], student_id))
            if cursor.fetchone():
                cursor.close()
                connection.close()
                return format_response({
                    'success': False,
                    'error': 'Email already exists'
                }, 409)
        
        # Build update query dynamically
        update_fields = []
        values = []
        
        allowed_fields = ['first_name', 'last_name', 'email', 'age', 'grade_level', 'phone', 'address']
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                values.append(data[field])
        
        if not update_fields:
            cursor.close()
            connection.close()
            return format_response({
                'success': False,
                'error': 'No valid fields to update'
            }, 400)
        
        values.append(student_id)
        query = f"UPDATE students SET {', '.join(update_fields)} WHERE id = %s"
        
        cursor.execute(query, values)
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return format_response({
            'success': True,
            'message': 'Student updated successfully'
        }, 200)
    
    except Error as e:
        return format_response({
            'success': False,
            'error': f'Database error: {str(e)}'
        }, 500)
    except Exception as e:
        return format_response({
            'success': False,
            'error': str(e)
        }, 500)

# DELETE - Delete a student
@app.route('/api/students/<int:student_id>', methods=['DELETE'])
@jwt_required()
def delete_student(student_id):
    """Delete a student record"""
    try:
        connection = get_db_connection()
        if not connection:
            return format_response({
                'success': False,
                'error': 'Database connection failed'
            }, 500)
        
        cursor = connection.cursor()
        
        # Check if student exists
        cursor.execute("SELECT id FROM students WHERE id = %s", (student_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            return format_response({
                'success': False,
                'error': 'Student not found'
            }, 404)
        
        # Delete student
        cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return format_response({
            'success': True,
            'message': 'Student deleted successfully'
        }, 200)
    
    except Error as e:
        return format_response({
            'success': False,
            'error': f'Database error: {str(e)}'
        }, 500)
    except Exception as e:
        return format_response({
            'success': False,
            'error': str(e)
        }, 500)

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return format_response({
        'success': True,
        'message': 'API is running'
    }, 200)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return format_response({
        'success': False,
        'error': 'Endpoint not found'
    }, 404)

@app.errorhandler(500)
def internal_error(error):
    return format_response({
        'success': False,
        'error': 'Internal server error'
    }, 500)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

