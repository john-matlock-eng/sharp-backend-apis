FROM public.ecr.aws/lambda/python:3.12

WORKDIR /var/task

COPY apis/source_ingestion/app/  /var/task/app
COPY lib/ /var/task/app/lib
COPY models/ /var/task/app/models
COPY services/ /var/task/app/services
COPY apis/source_ingestion/requirements.txt /var/task/

RUN pip install --no-cache-dir -r /var/task/requirements.txt
ENV PYTHONPATH="/var/task/app:${PYTHONPATH}"
CMD ["app.main.handler"]
