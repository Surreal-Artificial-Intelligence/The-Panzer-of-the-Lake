# app/Dockerfile

FROM python:3.12-slim

WORKDIR /app

# Install dependencies and clean up apt lists in one layer
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv
RUN pip install --no-cache-dir pipenv

COPY . .

# Install Python dependencies using Pipenv
RUN pipenv install --deploy --system

# Expose port 8501 for Streamlit
EXPOSE 8501

# Healthcheck for the Streamlit service
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Entry point to run the Streamlit app
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
