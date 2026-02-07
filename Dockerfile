FROM python:3.10

RUN useradd -m -u 1000 user

USER user

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

COPY --chown=user . $HOME/app
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Grant permissions for the database to be created/written
RUN mkdir -p $HOME/app && chown -R user:user $HOME/app
RUN chmod 777 $HOME/app

# Collect static files
RUN python manage.py collectstatic --no-input

EXPOSE 7860

# Start the application using Gunicorn (bind to 0.0.0.0:7860)
CMD ["gunicorn", "voting_system.wsgi:application", "--bind", "0.0.0.0:7860", "--workers", "2", "--timeout", "120"]
