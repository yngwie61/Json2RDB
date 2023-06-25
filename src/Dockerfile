# Use an appropriate base image depending on your requirements
FROM python:3.8

# Set the working directory inside the container
WORKDIR /app

# Copy the source code into the container
COPY httpd.py /app
COPY Json2RDB.py /app

# Install any necessary dependencies
# For example, if you have a requirements.txt file, uncomment the following line:
COPY requirements.txt /app
RUN pip install -r requirements.txt

# Specify the command to run when the container starts
CMD ["python", "httpd.py"]

