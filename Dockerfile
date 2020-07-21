FROM python:3.6.9-buster
RUN echo 'alias ll="ls -lart --color=auto"' >> ~/.bashrc
WORKDIR /app

COPY requirements.txt ./

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# For dev only
ENTRYPOINT ["tail", "-f", "/dev/null"]
#CMD [ "python", "carla.py", "--live" ]
