import logging
from typing import Dict, Any, List, Optional
from boto3.dynamodb.conditions import Key
from app.lib.dynamodb_controller import DynamoDBController
from app.models.quiz_schema import QuizCreate, QuizUpdate
from app.models.question_schema import QuestionModel
from app.lib.logging import log_and_handle_exceptions
from datetime import datetime, timezone
import os
from uuid import UUID

class QuizService:
    def __init__(self, dynamodb_controller: DynamoDBController):
        self.dynamodb_controller = dynamodb_controller
        self.logger = logging.getLogger(__name__)

    @log_and_handle_exceptions
    def create_quiz(self, quiz: QuizCreate) -> None:
        item = {
            'PK': 'QUIZ',
            'SK': f'COMMUNITY#{quiz.community_id}#QUIZ#{quiz.quiz_id}',
            'EntityType': 'Quiz',
            'CreatedAt': int(datetime.now(timezone.utc).timestamp()),
            'quiz_id': str(quiz.quiz_id),
            'community_id': str(quiz.community_id),
            'title': quiz.title,
            'description': quiz.description,
            'owner_ids': [str(owner_id) for owner_id in quiz.owner_ids],
        }
        self.dynamodb_controller.put_item(item)

    @log_and_handle_exceptions
    def get_quiz_metadata(self, community_id: str, quiz_id: str) -> Dict[str, Any]:
        partition_key = Key('PK').eq('QUIZ')
        sort_key_condition = Key('SK').eq(f'COMMUNITY#{community_id}#QUIZ#{quiz_id}')
        quizzes = self.dynamodb_controller.query_with_pagination(partition_key, sort_key_condition)[0]
        if not quizzes:
            return None
        return quizzes[0]


    @log_and_handle_exceptions
    def update_quiz(self, quiz_id: str, quiz_data: QuizUpdate) -> None:
        sk = f'COMMUNITY#{quiz_data.community_id}#QUIZ#{quiz_id}'
        update_data = quiz_data.dict(exclude_unset=True)
        self.dynamodb_controller.update_item('QUIZ', sk, update_data)

    @log_and_handle_exceptions
    def delete_quiz(self, community_id: str, quiz_id: str) -> None:
        # First, delete all questions for this quiz
        self.delete_all_questions_for_quiz(community_id, quiz_id)
        
        # Then, delete the quiz metadata
        sk = f'COMMUNITY#{community_id}#QUIZ#{quiz_id}'
        self.dynamodb_controller.delete_item('QUIZ', sk)

    @log_and_handle_exceptions
    def list_quizzes(self, community_id: str, limit: int = 10, last_evaluated_key: Optional[str] = None) -> (List[Dict[str, Any]], Optional[str]): # type: ignore
        partition_key = Key('PK').eq('QUIZ')
        sort_key_condition = Key('SK').begins_with(f'COMMUNITY#{community_id}#QUIZ#')
        print(partition_key, sort_key_condition)
        quizzes, next_token = self.dynamodb_controller.query_with_pagination(partition_key, sort_key_condition, limit=limit, last_evaluated_key=last_evaluated_key)
        return quizzes, next_token

    @log_and_handle_exceptions
    def get_questions_by_quiz_id(self, community_id: str, quiz_id: str, limit: int = 10, last_evaluated_key: Optional[str] = None) -> (List[Dict[str, Any]], Optional[str]):
        partition_key = Key('PK').eq('QUESTION')
        sort_key_condition = Key('SK').begins_with(f'COMMUNITY#{community_id}#QUIZ#{quiz_id}#QUESTION#')
        questions, next_token = self.dynamodb_controller.query_with_pagination(partition_key, sort_key_condition, limit=limit, last_evaluated_key=last_evaluated_key)
        return questions, next_token

    @log_and_handle_exceptions
    def create_question(self, community_id: str, quiz_id: str, question_data: QuestionModel) -> None:
        item = {
            'PK': 'QUESTION',
            'SK': f'COMMUNITY#{community_id}#QUIZ#{quiz_id}#QUESTION#{question_data.question_id}',
            'EntityType': 'Question',
            'question_id': str(question_data.question_id),
            'quiz_id': quiz_id,
            'community_id': community_id,
            'question_text': question_data.question_text,
            'options': question_data.options,
            'answer': question_data.answer,
            'CreatedAt': int(datetime.now(timezone.utc).timestamp()),
            "type": question_data.type
        }
        self.dynamodb_controller.put_item(item)

    @log_and_handle_exceptions
    def get_question(self, community_id: str, quiz_id: str, question_id: str) -> Dict[str, Any]:
        sk = f'COMMUNITY#{community_id}#QUIZ#{quiz_id}#QUESTION#{question_id}'
        return self.dynamodb_controller.get_item('QUESTION', sk)

    @log_and_handle_exceptions
    def update_question(self, community_id: str, quiz_id: str, question_id: str, question_data: QuestionModel) -> None:
        sk = f'COMMUNITY#{community_id}#QUIZ#{quiz_id}#QUESTION#{question_id}'
        
        update_data = {
            key: str(value) if isinstance(value, UUID) else value
            for key, value in question_data.dict(exclude_unset=True).items()
        }
    
        self.dynamodb_controller.update_item('QUESTION', sk, update_data)

    @log_and_handle_exceptions
    def delete_question(self, community_id: str, quiz_id: str, question_id: str) -> None:
        sk = f'COMMUNITY#{community_id}#QUIZ#{quiz_id}#QUESTION#{question_id}'
        self.dynamodb_controller.delete_item('QUESTION', sk)

    @log_and_handle_exceptions
    def delete_all_questions_for_quiz(self, community_id: str, quiz_id: str) -> None:
        partition_key = Key('PK').eq('QUESTION')
        sort_key_condition = Key('SK').begins_with(f'COMMUNITY#{community_id}#QUIZ#{quiz_id}#QUESTION#')
        last_evaluated_key = None

        while True:
            questions, last_evaluated_key = self.dynamodb_controller.query_with_pagination(
                partition_key, 
                sort_key_condition,
                last_evaluated_key=last_evaluated_key
            )
            for question in questions:
                self.delete_question(community_id, quiz_id, question['question_id'])
            
            if not last_evaluated_key:
                break

def get_quiz_service() -> QuizService:
    table_name = os.getenv('TABLE_NAME', 'sharp_app_data')
    dynamodb_controller = DynamoDBController(table_name)
    return QuizService(dynamodb_controller)