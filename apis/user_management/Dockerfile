FROM public.ecr.aws/lambda/python:3.12

WORKDIR /var/task
RUN pwd
RUN ls -la
COPY apis/user_management/app/ /var/task/app
RUN ls -la /var/task/app

COPY lib/ /var/task/lib
RUN ls -la /var/task/lib

COPY apis/user_management/requirements.txt /var/task/
RUN pip install --no-cache-dir -r /var/task/requirements.txt

RUN ls -la /var/task

CMD ["app.main.handler"]