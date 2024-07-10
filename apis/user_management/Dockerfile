FROM public.ecr.aws/lambda/python:3.12

WORKDIR /var/task

# Print the working directory and its contents
RUN pwd
RUN ls -la

# Copy application files and print contents
COPY apis/user_management/app/ /var/task/app
RUN echo "Contents of /var/task/app:" && ls -la /var/task/app

# Copy library files and print contents
COPY lib/ /var/task/lib
RUN echo "Contents of /var/task/lib:" && ls -la /var/task/lib

# Install dependencies and print final contents
COPY apis/user_management/requirements.txt /var/task/
RUN pip install --no-cache-dir -r /var/task/requirements.txt

RUN echo "Contents of /var/task:" && ls -la /var/task

CMD ["app.main.handler"]
