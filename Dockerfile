FROM python:3.10
# Set home to the user's home directory
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set the working directory to the user's home directory
WORKDIR $HOME/app

# Copy the current directory contents into the container at $HOME/app
COPY . $HOME/app

# permissions for start.sh
RUN chmod +x start.sh && sed -i 's/\r$//' start.sh

# Install requirements
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Grant permissions for the database to be created/written (even as root, good practice)
RUN mkdir -p $HOME/app && chmod -R 777 $HOME/app

# Collect static files
RUN python manage.py collectstatic --no-input

EXPOSE 7860

# Start the application using start.sh
CMD ["./start.sh"]
