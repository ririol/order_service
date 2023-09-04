FROM python:3.11

WORKDIR /code

COPY ./ /code/app/order_service

WORKDIR /code/app/order_service

RUN pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 80

ENV PYTHONPATH "${PYTHONPATH}:/code/app/"

WORKDIR /code/app/order_service/src

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]