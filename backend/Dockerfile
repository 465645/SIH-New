FROM python:3.12-slim

# tesseract-ocr is optional: without it the OCR endpoint degrades to the
# paste-text route rather than failing, but label photos need it.
RUN apt-get update \
 && apt-get install -y --no-install-recommends tesseract-ocr libgl1 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
