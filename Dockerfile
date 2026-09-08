FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# DEVELOPMENT — CURRENT

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]



# ============================================================
# PRODUCTION — FOR AWS
# ============================================================
# Production-ში Django-ს runserver-ის ნაცვლად ვიყენებთ Gunicorn-ს.
# როცა პროექტს AWS-ზე Production რეჟიმში გადავიყვანთ,
# ზემოთ არსებული CMD უნდა დავაკომენტაროთ
# და ეს CMD გავააქტიუროთ:
#
# CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]