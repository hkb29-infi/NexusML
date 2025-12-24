# NexusML

Distributed ML Training Platform

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd NexusML
    ```

2.  **Set up environment variables:**
    Create a `.env` file in the `backend` directory with the following content:
    ```
    DATABASE_URL=postgresql://nexus:dev_password@postgres:5432/nexusml
    REDIS_URL=redis://redis:6379
    ```

3.  **Build and run the application:**
    ```bash
    docker-compose up --build
    ```

4.  **Access the API:**
    The API will be available at `http://localhost:8000`.
    The OpenAPI documentation can be found at `http://localhost:8000/docs`.

5.  **Access the frontend:**
    The frontend will be available at `http://localhost:3000`.