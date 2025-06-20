# --- Stage 1: The Builder ---
# This stage installs all dependencies into a clean virtual environment.
# We use a slim version of Python 3.13 to match your development environment.
FROM python:3.13-slim-bullseye AS builder

# Set standard environment variables for Python in containers
ENV PYTHONDONTWRITEBYTECODE="1"
ENV PYTHONUNBUFFERED="1"

# Install uv for fast and efficient package management
RUN pip install uv

# Set the working directory for the build process
WORKDIR /app

# Create a virtual environment inside the container
RUN uv venv /opt/venv

# Activate the virtual environment for subsequent commands in this stage
ENV PATH="/opt/venv/bin:$PATH"

# Copy only the necessary files to install dependencies first
# This leverages Docker's layer caching for faster rebuilds.
COPY pyproject.toml ./
COPY src ./src

# Install all project dependencies, including our local 'cebollin' package
RUN uv pip install --no-cache-dir .


# --- Stage 2: The Final Production Image ---
# This stage creates the clean, final image.
FROM python:3.13-slim-bullseye AS final

# Set the same environment variables
ENV PYTHONDONTWRITEBYTECODE="1"
ENV PYTHONUNBUFFERED="1"

# Create a dedicated, non-root user for security best practices
RUN groupadd --system app && useradd --system --gid app app

# Copy the fully populated virtual environment from the 'builder' stage
COPY --from=builder /opt/venv /opt/venv

# Copy the application source code
COPY --from=builder --chown=app:app /app/src ./src

# Activate the virtual environment for the final container
ENV PATH="/opt/venv/bin:$PATH"

# Set the working directory for the running application
WORKDIR /home/app

# Switch to our secure, non-root user
USER app

# Expose the port that the application will run on
EXPOSE 8000

# The command to run the application when the container starts
# The host 0.0.0.0 is crucial to make it accessible from outside the container
CMD ["uvicorn", "cebollin.presentation.main:app", "--host", "0.0.0.0", "--port", "8000"]
