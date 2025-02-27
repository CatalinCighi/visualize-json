# Base image
FROM python:3.9-slim

# Set working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files into the container
COPY . ./

# Install the package in development mode
RUN pip install -e .

# Create a volume mount point for output
VOLUME /data

# Set the default command - now supports all the CLI options
ENTRYPOINT ["jsontree"]
CMD ["--directory", "/data", "--trim", "--visualize"]
