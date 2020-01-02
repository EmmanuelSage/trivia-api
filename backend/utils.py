from models import Question

def create_mock_question():
        """This creates a mock question in the database.

        This mock data is created to prevent having to drop 
        the database during the running of the test suite.
        """
        # insert mock qestion into Question constructor
        question = Question(
            question='This is a test question that should deleted',
            answer='this answer should be deleted',
            difficulty=1,
            category='1')

        # create a new mock question in the database
        question.insert()

        # return id of the mock question
        return question.id
