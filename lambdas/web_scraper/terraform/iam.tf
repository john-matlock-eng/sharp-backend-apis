data "aws_sqs_queue" "knowledge_source_processing_queue" {
  name = "knowledge_source_processing_queue"
}

resource "aws_lambda_permission" "allow_sqs_trigger" {
  statement_id  = "AllowSQSTrigger_web_scraper"
  action        = "lambda:InvokeFunction"
  function_name = "web_scraper"
  principal     = "sqs.amazonaws.com"
  source_arn    = data.aws_sqs_queue.knowledge_source_processing_queue.arn
}
