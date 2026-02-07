FROM python:3.10

# Set up a new user named "user" with user ID 1000
RUN useradd -m -u 1000 user

# Switch to the "user" user
USER user

# Set home to the user's home directory
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

# Set the working directory to the user's home directory
WORKDIR $HOME/app

# Copy the current directory contents into the container at $HOME/app setting the owner to the user
COPY --chown=user . $HOME/app

# Install requirements
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Collect static files
RUN python manage.py collectstatic --no-input

# Expose port 7860 (Standard for HF Spaces)
EXPOSE 7860

# Start the application using Gunicorn on port 7860
CMD ["gunicorn", "voting_system.wsgi:application", "--bind", "0.0.0.0:7860"]
