data "aws_sqs_queue" "knowledge_source_url_initial_ingestion_queue" {
  name = "knowledge_source_url_initial_ingestion_queue"
}

data "aws_sqs_queue" "knowledge_source_chunk_processing_queue" {
  name = "knowledge_source_chunk_processing_queue"
}

resource "aws_lambda_permission" "allow_sqs_trigger" {
  statement_id  = "AllowSQSTrigger_web_scraper"
  action        = "lambda:InvokeFunction"
  function_name = "web_scraper"
  principal     = "sqs.amazonaws.com"
  source_arn    = data.aws_sqs_queue.knowledge_source_url_initial_ingestion_queue.arn
}

resource "aws_iam_policy" "lambda_sqs_policy" {
  name        = "web_scraper_sqs_policy"
  description = "IAM policy for Lambda to read from SQS"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ],
        Resource = "${data.aws_sqs_queue.knowledge_source_url_initial_ingestion_queue.arn}"
      },
      {
        Effect = "Allow",
        Action = [
          "sqs:SendMessage"
        ],
        Resource = "${data.aws_sqs_queue.knowledge_source_chunk_processing_queue.arn}"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_sqs_attachment" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_sqs_policy.arn
}
