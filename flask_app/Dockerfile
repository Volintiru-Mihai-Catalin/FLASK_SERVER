FROM python:latest

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY flask_app.py ./

ENV DB_HOST=flask_db
ENV DB_PORT=5432
ENV DB_NAME=postgres
ENV DB_USER=postgres
ENV DB_PASSWORD=postgres

EXPOSE 6000

CMD ["flask", "--app", "flask_app.py", "run", "--host=0.0.0.0", "--port=6000"]