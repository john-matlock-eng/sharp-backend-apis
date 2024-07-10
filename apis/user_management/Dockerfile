FROM public.ecr.aws/lambda/python:3.12

WORKDIR /var/task

COPY apis/user_management/app/ /var/task/app
COPY lib/ /var/task/lib

COPY apis/user_management/requirements.txt /var/task/
RUN pip install --no-cache-dir -r /var/task/requirements.txt

CMD ["app.main.handler"]
