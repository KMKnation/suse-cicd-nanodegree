FROM python:2.7.18
ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip
RUN mkdir /techtrends
COPY ./techtrends/. /techtrends/
WORKDIR /techtrends
RUN pip install -r requirements.txt
RUN python init_db.py
EXPOSE 3111

CMD ["python", "app.py", "0.0.0.0:7111"]