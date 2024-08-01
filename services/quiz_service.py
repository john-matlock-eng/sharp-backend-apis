from app.lib.dynamodb_controller import DynamoDBController
from app.models.quiz_schema import QuizCreate
from typing import Dict, Any, List

class QuizService:
    def __init__(self, dynamodb_controller: DynamoDBController):
        self.dynamodb_controller = dynamodb_controller

    def create_quiz(self, quiz: QuizCreate) -> None:
        item = {
            'PK': 'COMMUNITY',
            'SK': f'COMMUNITY#{quiz.community_id}#QUIZ#{quiz.quiz_id}',
            'EntityType': 'Quiz',
            'CreatedAt': quiz.created_at,
            'quiz_id': str(quiz.quiz_id),
            'community_id': str(quiz.community_id),
            'topic': quiz.topic,
            'description': quiz.description,
            'questions': [q.dict() for q in quiz.questions],
        }
        self.dynamodb_controller.put_item(item)

    def get_quiz(self, community_id: str, quiz_id: str) -> Dict[str, Any]:
        sk = f'COMMUNITY#{community_id}#QUIZ#{quiz_id}'
        return self.dynamodb_controller.get_item('COMMUNITY', sk)

    def update_quiz(self, community_id: str, quiz_id: str, update_data: Dict[str, Any]) -> None:
        sk = f'COMMUNITY#{community_id}#QUIZ#{quiz_id}'
        self.dynamodb_controller.update_item('COMMUNITY', sk, update_data)

    def delete_quiz(self, community_id: str, quiz_id: str) -> None:
        sk = f'COMMUNITY#{community_id}#QUIZ#{quiz_id}'
        self.dynamodb_controller.delete_item('COMMUNITY', sk)

    def list_quizzes(self, community_id: str) -> List[Dict[str, Any]]:
        partition_key = Key('PK').eq('COMMUNITY')
        sort_key_condition = Key('SK').begins_with(f'COMMUNITY#{community_id}#QUIZ#')
        return self.dynamodb_controller.query_with_pagination(partition_key, sort_key_condition)[0]
