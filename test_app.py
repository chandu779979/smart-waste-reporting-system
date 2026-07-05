import unittest
import os
import io
from app import create_app
from extensions import db
from models.municipality import Municipality
from models.citizen import Citizen
from models.admin import Admin
from models.complaint import Complaint
from models.status_history import ComplaintStatusHistory

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'test_uploads')
    SECRET_KEY = 'testsecretkey'
    GOOGLE_MAPS_API_KEY = 'test-maps-key'
    MAX_CONTENT_LENGTH = 5242880
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

class SmartWasteSystemTestCase(unittest.TestCase):
    def setUp(self):
        # Configure app for testing with TestConfig
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Build memory database and seed municipalities
        db.create_all()
        self.seed_test_municipalities()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
        # Remove temporary testing uploads folder
        test_upload_folder = self.app.config['UPLOAD_FOLDER']
        if os.path.exists(test_upload_folder):
            import shutil
            shutil.rmtree(test_upload_folder)

    def seed_test_municipalities(self):
        self.m1 = Municipality(name="Anantapur Municipality")
        self.m2 = Municipality(name="Kadapa Municipality")
        self.m3 = Municipality(name="Kurnool Municipality")
        db.session.add_all([self.m1, self.m2, self.m3])
        db.session.commit()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Smart Waste', response.data)
        self.assertIn(b'System Workflow', response.data)

    def test_citizen_registration_and_login(self):
        # Test Registration
        response = self.client.post('/register/citizen', data={
            'name': 'Jane Doe',
            'email': 'jane@gmail.com',
            'phone': '9876543210',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Citizen registration successful! Please log in.', response.data)
        
        # Test Login
        response = self.client.post('/login/citizen', data={
            'email': 'jane@gmail.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome back, Jane Doe!', response.data)
        self.assertIn(b'Citizen Dashboard', response.data)

    def test_admin_registration_and_login(self):
        # Test Admin registration for Anantapur Municipality
        response = self.client.post('/register/admin', data={
            'name': 'Officer John',
            'email': '',  # Auto-assigned by server
            'phone': '9000012345',
            'municipality_id': self.m1.id,
            'password': 'adminpass',
            'confirm_password': 'adminpass'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin registration successful! Please log in.', response.data)
        
        # Test Admin Login
        response = self.client.post('/login/admin', data={
            'email': 'admin@anantapur.gov.in',
            'password': 'adminpass'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome back Admin, Officer John!', response.data)
        self.assertIn(b'Anantapur Municipality Admin', response.data)

    def test_complaint_submission_flow_and_history(self):
        # 1. Setup reporting citizen
        self.client.post('/register/citizen', data={
            'name': 'Jane Doe',
            'email': 'jane@gmail.com',
            'phone': '9876543210',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        self.client.post('/login/citizen', data={
            'email': 'jane@gmail.com',
            'password': 'password123'
        })
        
        # 2. Submit complaint with details
        data = {
            'title': 'Garbage pile near central park',
            'description': 'A large pile of household garbage has accumulated near the entrance.',
            'waste_category': 'Garbage Pile',
            'municipality_id': self.m1.id,
            'latitude': '14.6819',
            'longitude': '77.6006',
            'address': 'Central Park, Anantapur',
            'image': (io.BytesIO(b'dummy_image_data_here'), 'test_image.jpg')
        }
        response = self.client.post('/citizen/complaint/submit', data=data, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your complaint has been submitted successfully!', response.data)
        
        # 3. Assert DB insertion
        complaint = Complaint.query.first()
        self.assertIsNotNone(complaint)
        self.assertEqual(complaint.title, 'Garbage pile near central park')
        self.assertEqual(complaint.status, 'Pending')
        self.assertEqual(complaint.latitude, 14.6819)
        self.assertEqual(complaint.longitude, 77.6006)
        
        # 4. Assert initial history log
        history = ComplaintStatusHistory.query.filter_by(complaint_id=complaint.id).first()
        self.assertIsNotNone(history)
        self.assertIsNone(history.previous_status)
        self.assertEqual(history.new_status, 'Pending')
        self.assertEqual(history.updated_by_name, 'Jane Doe')
        
        # 5. Assert dashboard displays the complaint
        response = self.client.get('/citizen/dashboard')
        self.assertIn(b'Garbage pile near central park', response.data)
        
        # 6. Log out citizen, then register and log in Admin 1 for Anantapur
        self.client.get('/logout')
        self.client.post('/register/admin', data={
            'name': 'Officer John',
            'email': '',  # Auto-assigned by server
            'phone': '9000012345',
            'municipality_id': self.m1.id,
            'password': 'adminpass',
            'confirm_password': 'adminpass'
        })
        self.client.post('/login/admin', data={
            'email': 'admin@anantapur.gov.in',
            'password': 'adminpass'
        })
        
        # 7. Check if complaint is visible to Admin 1
        response = self.client.get('/admin/dashboard')
        self.assertIn(b'Garbage pile near central park', response.data)
        
        # 8. Check that Admin 2 for Kadapa Municipality does NOT see this complaint
        self.client.get('/logout') # Logout Officer John
        self.client.post('/register/admin', data={
            'name': 'Officer Bob',
            'email': '',  # Auto-assigned by server
            'phone': '9000054321',
            'municipality_id': self.m2.id,
            'password': 'bobpass',
            'confirm_password': 'bobpass'
        })
        self.client.post('/login/admin', data={
            'email': 'admin@kadapa.gov.in',
            'password': 'bobpass'
        })
        response = self.client.get('/admin/dashboard')
        self.assertNotIn(b'Garbage pile near central park', response.data)
        
        # 9. Relogin Admin 1 to update status
        self.client.get('/logout')
        self.client.post('/login/admin', data={
            'email': 'admin@anantapur.gov.in',
            'password': 'adminpass'
        })
        
        # 10. Admin updates status to 'In Progress' with comment
        response = self.client.post(f'/admin/complaint/{complaint.id}', data={
            'status': 'In Progress',
            'comment': 'Dispatched crew with garbage collection truck.'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Complaint status updated successfully from Pending to In Progress!', response.data)
        
        # 11. Verify status history audit records
        history_records = ComplaintStatusHistory.query.filter_by(complaint_id=complaint.id).order_by(ComplaintStatusHistory.timestamp.desc()).all()
        self.assertEqual(len(history_records), 2)
        self.assertEqual(history_records[0].previous_status, 'Pending')
        self.assertEqual(history_records[0].new_status, 'In Progress')
        self.assertEqual(history_records[0].comment, 'Dispatched crew with garbage collection truck.')
        self.assertEqual(history_records[0].updated_by_name, 'Officer John')

if __name__ == '__main__':
    unittest.main()
