import unittest
import json
from app import app
import mysql.connector
from mysql.connector import Error

class StudentAPITestCase(unittest.TestCase):
    """Test cases for Student Management API"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test client and database"""
        cls.client = app.test_client()
        cls.client.testing = True
        cls.access_token = None
        
        # Get authentication token
        cls._get_auth_token()
    
    @classmethod
    def _get_auth_token(cls):
        """Get JWT token for authentication"""
        response = cls.client.post('/api/auth/login',
                                   data=json.dumps({
                                       'username': 'admin',
                                       'password': 'admin123'
                                   }),
                                   content_type='application/json')
        data = json.loads(response.data)
        cls.access_token = data.get('access_token')
    
    def get_auth_headers(self):
        """Get authorization headers"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    # Authentication Tests
    def test_01_login_success(self):
        """Test successful login"""
        response = self.client.post('/api/auth/login',
                                   data=json.dumps({
                                       'username': 'admin',
                                       'password': 'admin123'
                                   }),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('access_token', data)
    
    def test_02_login_failure(self):
        """Test failed login with wrong credentials"""
        response = self.client.post('/api/auth/login',
                                   data=json.dumps({
                                       'username': 'admin',
                                       'password': 'wrong_password'
                                   }),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_03_login_missing_credentials(self):
        """Test login with missing credentials"""
        response = self.client.post('/api/auth/login',
                                   data=json.dumps({}),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    # CREATE Tests
    def test_04_create_student_success(self):
        """Test creating a student successfully"""
        student_data = {
            'first_name': 'Test',
            'last_name': 'Student',
            'email': f'test{unittest.TestCase.id}@example.com',
            'age': 18,
            'grade_level': 12,
            'phone': '1234567890',
            'address': '123 Test St'
        }
        
        response = self.client.post('/api/students',
                                   data=json.dumps(student_data),
                                   headers=self.get_auth_headers())
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('student_id', data)
    
    def test_05_create_student_missing_fields(self):
        """Test creating student with missing required fields"""
        student_data = {
            'first_name': 'Test',
            'email': 'incomplete@example.com'
        }
        
        response = self.client.post('/api/students',
                                   data=json.dumps(student_data),
                                   headers=self.get_auth_headers())
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('errors', data)
    
    def test_06_create_student_invalid_email(self):
        """Test creating student with invalid email"""
        student_data = {
            'first_name': 'Test',
            'last_name': 'Student',
            'email': 'invalid-email',
            'age': 18,
            'grade_level': 12
        }
        
        response = self.client.post('/api/students',
                                   data=json.dumps(student_data),
                                   headers=self.get_auth_headers())
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_07_create_student_invalid_age(self):
        """Test creating student with invalid age"""
        student_data = {
            'first_name': 'Test',
            'last_name': 'Student',
            'email': 'test_age@example.com',
            'age': 200,
            'grade_level': 12
        }
        
        response = self.client.post('/api/students',
                                   data=json.dumps(student_data),
                                   headers=self.get_auth_headers())
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_08_create_student_invalid_grade(self):
        """Test creating student with invalid grade level"""
        student_data = {
            'first_name': 'Test',
            'last_name': 'Student',
            'email': 'test_grade@example.com',
            'age': 18,
            'grade_level': 15
        }
        
        response = self.client.post('/api/students',
                                   data=json.dumps(student_data),
                                   headers=self.get_auth_headers())
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_09_create_student_without_auth(self):
        """Test creating student without authentication"""
        student_data = {
            'first_name': 'Test',
            'last_name': 'Student',
            'email': 'test@example.com',
            'age': 18,
            'grade_level': 12
        }
        
        response = self.client.post('/api/students',
                                   data=json.dumps(student_data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 401)
    
    # READ Tests
    def test_10_get_all_students(self):
        """Test getting all students"""
        response = self.client.get('/api/students',
                                  headers=self.get_auth_headers())
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('students', data)
        self.assertIn('count', data)
    
    def test_11_get_student_by_id(self):
        """Test getting a specific student by ID"""
        # First create a student
        student_data = {
            'first_name': 'Get',
            'last_name': 'Test',
            'email': 'gettest@example.com',
            'age': 17,
            'grade_level': 11
        }
        
        create_response = self.client.post('/api/students',
                                          data=json.dumps(student_data),
                                          headers=self.get_auth_headers())
        
        create_data = json.loads(create_response.data)
        student_id = create_data['student_id']
        
        # Now get the student
        response = self.client.get(f'/api/students/{student_id}',
                                  headers=self.get_auth_headers())
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('student', data)
        self.assertEqual(data['student']['email'], 'gettest@example.com')
    
    def test_12_get_nonexistent_student(self):
        """Test getting a student that doesn't exist"""
        response = self.client.get('/api/students/999999',
                                  headers=self.get_auth_headers())
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_13_search_students_by_name(self):
        """Test searching students by name"""
        response = self.client.get('/api/students?name=Test',
                                  headers=self.get_auth_headers())
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_14_search_students_by_grade(self):
        """Test searching students by grade level"""
        response = self.client.get('/api/students?grade_level=12',
                                  headers=self.get_auth_headers())
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_15_search_students_by_email(self):
        """Test searching students by email"""
        response = self.client.get('/api/students?email=test',
                                  headers=self.get_auth_headers())
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    # UPDATE Tests
    def test_16_update_student_success(self):
        """Test updating a student successfully"""
        # Create a student first
        student_data = {
            'first_name': 'Update',
            'last_name': 'Test',
            'email': 'updatetest@example.com',
            'age': 16,
            'grade_level': 10
        }
        
        create_response = self.client.post('/api/students',
                                          data=json.dumps(student_data),
                                          headers=self.get_auth_headers())
        
        create_data = json.loads(create_response.data)
        student_id = create_data['student_id']
        
        # Update the student
        update_data = {
            'first_name': 'Updated',
            'age': 17,
            'grade_level': 11
        }
        
        response = self.client.put(f'/api/students/{student_id}',
                                  data=json.dumps(update_data),
                                  headers=self.get_auth_headers())
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_17_update_nonexistent_student(self):
        """Test updating a student that doesn't exist"""
        update_data = {
            'first_name': 'Updated'
        }
        
        response = self.client.put('/api/students/999999',
                                  data=json.dumps(update_data),
                                  headers=self.get_auth_headers())
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_18_update_student_invalid_data(self):
        """Test updating student with invalid data"""
        # Create a student first
        student_data = {
            'first_name': 'Invalid',
            'last_name': 'Update',
            'email': 'invalidupdate@example.com',
            'age': 16,
            'grade_level': 10
        }
        
        create_response = self.client.post('/api/students',
                                          data=json.dumps(student_data),
                                          headers=self.get_auth_headers())
        
        create_data = json.loads(create_response.data)
        student_id = create_data['student_id']
        
        # Try to update with invalid email
        update_data = {
            'email': 'invalid-email-format'
        }
        
        response = self.client.put(f'/api/students/{student_id}',
                                  data=json.dumps(update_data),
                                  headers=self.get_auth_headers())
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_19_update_student_no_data(self):
        """Test updating student with no data"""
        response = self.client.put('/api/students/1',
                                  data=json.dumps({}),
                                  headers=self.get_auth_headers())
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    # DELETE Tests
    def test_20_delete_student_success(self):
        """Test deleting a student successfully"""
        # Create a student first
        student_data = {
            'first_name': 'Delete',
            'last_name': 'Test',
            'email': 'deletetest@example.com',
            'age': 18,
            'grade_level': 12
        }
        
        create_response = self.client.post('/api/students',
                                          data=json.dumps(student_data),
                                          headers=self.get_auth_headers())
        
        create_data = json.loads(create_response.data)
        student_id = create_data['student_id']
        
        # Delete the student
        response = self.client.delete(f'/api/students/{student_id}',
                                     headers=self.get_auth_headers())
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_21_delete_nonexistent_student(self):
        """Test deleting a student that doesn't exist"""
        response = self.client.delete('/api/students/999999',
                                     headers=self.get_auth_headers())
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_22_delete_student_without_auth(self):
        """Test deleting student without authentication"""
        response = self.client.delete('/api/students/1',
                                     content_type='application/json')
        
        self.assertEqual(response.status_code, 401)
    
    # Format Tests
    def test_23_get_json_format(self):
        """Test getting data in JSON format"""
        response = self.client.get('/api/students?format=json',
                                  headers=self.get_auth_headers())
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
    
    def test_24_get_xml_format(self):
        """Test getting data in XML format"""
        response = self.client.get('/api/students?format=xml',
                                  headers=self.get_auth_headers())
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/xml')
        self.assertIn(b'<?xml', response.data)
    
    def test_25_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/api/health')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)