import unittest
import json
from server import create_app
from models import setup_db, Todo, TodoList

class TestCase(unittest.TestCase):
    def setUp(self):
        # self: Propiedades de la clase
        # La instancia de la aplicación y un cliente
        self.app = create_app()
        self.client = self.app.test_client

        # CREATING A NEW DATABASE FOR TESTING
        self.database_path = 'postgresql://postgres:conejowas12345@localhost:5432/todoapp10_test'

        setup_db(self.app, self.database_path) # setup_db(app, database_path)
    
    def test_get_todos_success(self):
        response = self.client().get('/todos')
        print("Response.data (BSON): ", response.data) # Binary JSON (BSON)
        print("Response.status_code: ", response.status_code)
        # Dedeserializar (turn binary format into data)
        data = json.loads(response.data)
        print("Response.data (JSON): ", data)
        # TESTING
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)


    def test_update_todo_success(self):
        response = self.client().patch('/todos/1', json = {'description': 'HIT ON GIRL'})
        data = json.loads(response.data)

        print("Response.data (JSON): ", data)

        # TESTING
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['id'], '1')

    def test_delete_todo_success(self):
        response = self.client().delete('/todos/1', json = {'description': 'HIT ON GIRL'})
        
        data = json.loads(response.data)


# python -m unittest
if __name__ == '__main__':
    unittest.main()





