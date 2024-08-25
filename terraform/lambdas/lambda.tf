resource "aws_lambda_function" "knowledge_source_processing_lambda" {
  function_name = "knowledge_source_processing_lambda"
  runtime       = "python3.11"
  handler       = "lambda_function.lambda_handler"
  role          = aws_iam_role.knowledge_source_processing_lambda_role.arn
  memory_size   = 256
  timeout       = 60

  environment {
    variables = {
      SFN_ARN = aws_sfn_state_machine.knowledge_source_processing_sfn.arn
    }
  }

  # Assuming your code is stored in a zip file or S3
  filename = "path/to/your/deployment-package.zip"

  depends_on = [aws_iam_role_policy.knowledge_source_processing_lambda_policy]
}

resource "aws_iam_role" "knowledge_source_processing_lambda_role" {
  name = "knowledge_source_processing_lambda_role"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Action" : "sts:AssumeRole",
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "knowledge_source_processing_lambda_policy" {
  name = "knowledge_source_processing_lambda_policy"
  role = aws_iam_role.knowledge_source_processing_lambda_role.id
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "states:StartExecution" # Permission to start the Step Function
        ],
        "Resource" : aws_sfn_state_machine.knowledge_source_processing_sfn.arn
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        "Resource" : "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_sfn_state_machine" "knowledge_source_processing_sfn" {
  name       = "knowledge_source_processing_sfn"
  role_arn   = aws_iam_role.sfn_role.arn
  definition = <<-EOF
  {
    "Comment": "Knowledge Source Processing Workflow",
    "StartAt": "CreateKnowledgeSourceEntry",
    "States": {
      "CreateKnowledgeSourceEntry": {
        "Type": "Task",
        "Resource": "${aws_lambda_function.create_knowledge_source_entry_lambda.arn}",
        "Next": "ScrapeContent"
      },
      "ScrapeContent": {
        "Type": "Task",
        "Resource": "${aws_lambda_function.scrape_content_lambda.arn}",
        "Next": "ProcessContent"
      },
      "ProcessContent": {
        "Type": "Task",
        "Resource": "${aws_lambda_function.process_content_lambda.arn}",
        "Next": "StoreChunks"
      },
      "StoreChunks": {
        "Type": "Task",
        "Resource": "${aws_lambda_function.store_chunks_lambda.arn}",
        "Next": "CombineAndCleanUpContent"
      },
      "CombineAndCleanUpContent": {
        "Type": "Task",
        "Resource": "${aws_lambda_function.combine_cleanup_lambda.arn}",
        "Next": "StoreCombinedOutput"
      },
      "StoreCombinedOutput": {
        "Type": "Task",
        "Resource": "${aws_lambda_function.store_combined_output_lambda.arn}",
        "Next": "UpdateKnowledgeSourceStatus"
      },
      "UpdateKnowledgeSourceStatus": {
        "Type": "Task",
        "Resource": "${aws_lambda_function.update_status_lambda.arn}",
        "End": true
      }
    }
  }
  EOF
}
