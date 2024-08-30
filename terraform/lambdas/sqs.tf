resource "aws_sqs_queue" "knowledge_source_url_initial_ingestion_queue" {
  name                       = "knowledge_source_url_initial_ingestion_queue"
  visibility_timeout_seconds = 60     # 1 minute
  message_retention_seconds  = 345600 # 4 days
  max_message_size           = 262144 # 256 KB
  delay_seconds              = 0      # No delivery delay
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.knowledge_source_processing_dlq.arn
    maxReceiveCount     = 5
  })
}

resource "aws_sqs_queue" "knowledge_source_url_initial_ingestion_dlq" {
  name                       = "knowledge_source_url_initial_ingestion_dlq"
  visibility_timeout_seconds = 60      # Match the primary queue
  message_retention_seconds  = 1209600 # 14 days retention for DLQ
  max_message_size           = 262144  # 256 KB
}

resource "aws_sqs_queue" "knowledge_source_chunk_processing_queue" {
  name                       = "knowledge_source_chunk_processing_queue"
  visibility_timeout_seconds = 60     # 1 minute
  message_retention_seconds  = 345600 # 4 days
  max_message_size           = 262144 # 256 KB
  delay_seconds              = 0      # No delivery delay
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.knowledge_source_processing_dlq.arn
    maxReceiveCount     = 5
  })
}

resource "aws_sqs_queue" "knowledge_source_chunk_processing_dlq" {
  name                       = "knowledge_source_chunk_processing_dlq"
  visibility_timeout_seconds = 60      # Match the primary queue
  message_retention_seconds  = 1209600 # 14 days retention for DLQ
  max_message_size           = 262144  # 256 KB
}

# resource "aws_lambda_event_source_mapping" "knowledge_source_processing_trigger" {
#   event_source_arn = aws_sqs_queue.knowledge_source_processing_queue.arn
#   function_name    = aws_lambda_function.knowledge_source_processing_lambda.arn
#   enabled          = true
#   batch_size       = 1

#   depends_on = [aws_lambda_permission.allow_knowledge_source_processing_lambda]
# }

# resource "aws_lambda_permission" "allow_knowledge_source_processing_lambda" {
#   statement_id  = "AllowKnowledgeSourceProcessingLambdaInvoke"
#   action        = "lambda:InvokeFunction"
#   function_name = aws_lambda_function.knowledge_source_processing_lambda.arn
#   principal     = "sqs.amazonaws.com"
#   source_arn    = aws_sqs_queue.knowledge_source_processing_queue.arn
# }
