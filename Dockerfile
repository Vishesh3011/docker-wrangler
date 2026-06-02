# Uses 3.12-slim instead of 3.12 for stripping unnecessary system packages. Smaller image = faster pull & lower attack surface
FROM python:3.12-slim

# Set working directory to be app inside container
WORKDIR /app

# Copies the requirements first as we want dependencies to be installed first as Docker caches its layer
# If there's no change in requirements then docker would directly use the cached pip layer. Thus only changed layers rebuild
# This results into faster builds.
COPY requirements.txt .
# No cache-dir flag is used to avoid caching the packages in docker layer which would unnecessarily increase the image size.
RUN pip install --no-cache-dir -r requirements.txt

# Copying the rest of source code
COPY . .

# Exposes port 8000 for app to listens on
EXPOSE 8000

# The CLI command to run the app
# Each space separated value is treated as a separate argument.
CMD ["python", "app/app.py"]