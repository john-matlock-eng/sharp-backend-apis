FROM public.ecr.aws/lambda/python:3.12

WORKDIR /var/task

COPY cognito_post_confirmation/app/ /var/task/app
COPY lib/ /var/task/app/lib
COPY services/ /var/task/app/services
COPY cognito_post_confirmation/requirements.txt /var/task/
RUN pip install --no-cache-dir -r /var/task/requirements.txt

CMD ["app.post_confirmation_handler.handler"]
