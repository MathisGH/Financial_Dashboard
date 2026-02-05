# Image
FROM python:3.9-slim

# Create the folder /app in the container and set it as the working directory
WORKDIR /app

# Install the dependencies
COPY requirements_docker.txt .

# --no-cache-dir to reduce the image size
RUN pip install --no-cache-dir -r requirements_docker.txt

# Copy the rest of the code to the container
COPY . .

# Expose the port that the app will run on
EXPOSE 8000

# Command to run the app
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]