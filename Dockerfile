FROM python:3.10.7

COPY . /app

WORKDIR /app

RUN pip install --upgrade pip && \
    pip install -r /app/requirements.txt && \
    pip install setuptools==57.0.0 --force-reinstall && \
    pip install wheel==0.36.2 --force-reinstall && \
    pip uninstall comtypes && \
    pip install --no-cache-dir comtypes && \
    pip install pycrypto --force-reinstall

RUN pip install poetry==1.5.1

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

RUN pip install uvicorn

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]