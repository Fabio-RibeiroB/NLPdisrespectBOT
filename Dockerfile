FROM python:3
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "sentimental_analysis_bot.py"]
