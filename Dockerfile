FROM python:3.10.6-slim-buster

# Set the working directory in the container
WORKDIR /code

# Copy the requirements file into the container
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on (change if different)
EXPOSE 5000

# Define environment variable (if needed)
ENV FLASK_ENV=production

# Run the application
CMD ["python", "run.py"]