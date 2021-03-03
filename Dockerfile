FROM python:3.7

WORKDIR /src

COPY requirements.txt .
COPY wait-for-it.sh .

RUN pip install -r requirements.txt
RUN chmod +x ./wait-for-it.sh

COPY src/ .

ENV PUBLIC_KEY <YOUR_PUBLIC_KEY>
ENV PRIVATE_KEY <YOUR_PRIVATE_KEY>

CMD ["./wait-for-it.sh", "db:3306", "--", "python", "marvel.py"]