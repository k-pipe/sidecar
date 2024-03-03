FROM python:3.10.11-alpine
ADD requirements.txt ./
RUN apk --no-cache add py-pip && pip install --no-cache-dir -r requirements.txt
ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
RUN mkdir $APP_HOME
ADD run.sh *.py $APP_HOME
WORKDIR $APP_HOME
ENTRYPOINT ["/app/run.sh"]
