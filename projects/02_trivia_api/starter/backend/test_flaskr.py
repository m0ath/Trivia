import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
        # new question
        self.new_question = {
            'question': 'who is the best ?',
            'answer': 'Me :D',
            'difficulty': '1',
            'category': '1'
        }

        # quiz
        self.quiz = {
            'previous_questions': ['1', '2'],
            'quiz_category': {
                'id': '1'
            }
        }

        # quiz with out questions
        self.bad_quiz = {
            'previous_questions': '',
            'quiz_category': {
                'id': '1000'
            }
        }
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 10)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])

    def test_404_page_not_found(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Opss! Not found it')

    def test_10_questions_per_page(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 10)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])

    def test_categories_generated(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_delete_question(self):
        question = Question(question=self.new_question['question'], answer=self.new_question['answer'], category=self.new_question['category'], difficulty=self.new_question['difficulty'])
        question.insert()

        res = self.client().delete(f'/questions/{question.id}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question.id)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_404_delete_question_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable, try one more time :D')

    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_405_if_question_not_allowed(self):
        res = self.client().post('/questions/45', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method Not Allowed here :(')
        
    def test_get_question_search_with_results(self):
        res = self.client().post('/search', json={'searchTerm': 'Which'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 6)
        self.assertTrue(data['total_questions'])

    def test_get_question_search_without_results(self):
        res = self.client().post('/search', json={'searchTerm': 'no body'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Opss! Not found it')

    def test_422_when_send_empty_search(self):
        res = self.client().post('/search', json={'searchTerm': ''})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable, try one more time :D')   

    def test_get_questions_by_catgeory(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 10)
        self.assertEqual(data['id_category'], 1)
        self.assertTrue(data['current_category'])
        self.assertTrue(data['total_questions'])

    def test_404_get_questions_by_catgeory_not_exist(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Opss! Not found it')

    def test_play_quizzes(self):
        res = self.client().post('/quizzes', json=self.quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertTrue(data['category_id'])
        self.assertTrue(data['all_selection'])


    def test_play_quiz_without_questions(self):
        res = self.client().post('/quizzes', json=self.bad_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable, try one more time :D')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()