FROM python:3.10

RUN useradd -m -u 1000 user

USER user

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy the current directory contents into the container at $HOME/app setting the owner to the user
COPY --chown=user . $HOME/app

# permissions for start.sh
RUN chmod +x start.sh && sed -i 's/\r$//' start.sh

# Install requirements
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Grant permissions for the database to be created/written
# Ensure the user has full control over the app directory
RUN chown -R user:user $HOME/app && chmod -R 777 $HOME/app

# Collect static files
RUN python manage.py collectstatic --no-input

EXPOSE 7860

# Start the application using start.sh
CMD ["./start.sh"]
