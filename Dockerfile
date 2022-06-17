FROM python:3.6

RUN adduser --system --uid 999 spaceteam
USER spaceteam

WORKDIR /app

COPY --chown=999:999 requirements*.txt ./
RUN pip install --no-cache-dir --user -r requirements.txt

COPY --chown=999:999 . .

CMD ["python3", "spaceteam.py"]
