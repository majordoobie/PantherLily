FROM python:3.7-buster
WORKDIR /code
RUN echo 'alias ll="ls -lart --color=auto"' >> ~/.bashrc

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["tail", "-f", "/dev/null"]
#CMD [ "python", "carla.py", "--live" ]
