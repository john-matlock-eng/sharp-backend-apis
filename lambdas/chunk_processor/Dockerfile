FROM public.ecr.aws/lambda/python:3.12

WORKDIR /var/task

# Copy the service-specific files
COPY lambdas/web_scraper/app/ /var/task/app/

# Copy the common directories
COPY models/ /var/task/app/models/
COPY lib/ /var/task/app/lib/
COPY services/ /var/task/app/services/
COPY lambdas/web_scraper/requirements.txt /var/task/


# Install dependencies
COPY lambdas/web_scraper/requirements.txt /var/task/
RUN pip install --no-cache-dir -r /var/task/requirements.txt

# Set the PYTHONPATH to include the /var/task/app directory
ENV PYTHONPATH="/var/task/app:${PYTHONPATH}"

# Set the Lambda handler
CMD ["app.web_scraper.lambda_handler"]
