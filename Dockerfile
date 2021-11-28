FROM python:3.7.12

COPY requirements.txt .
RUN pip install -r ./requirements.txt

WORKDIR /api
COPY . .
RUN make check && make test
CMD make run