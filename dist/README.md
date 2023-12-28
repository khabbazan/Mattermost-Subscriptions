## How to Use

### Prerequisites
- Docker and Docker Compose installed on your machine.

### Setup

1. **Place the Files**: Ensure that the `Dockerfile` and `docker-compose.yml` are placed in the root directory of your Django project.

2. **Create a .env File**: Make sure you have a `.env` file in the same directory. This file should contain all the necessary environment variables for your application.

### Building and Running the Application

1. **Open a Terminal**: Navigate to the directory where your `Dockerfile` and `docker-compose.yml` are located.

2. **Build and Run Containers**: Execute the following command to build your Docker images and start the containers:

    ```bash
    docker-compose up --build
    ```

    The `--build` flag is used to build the Docker images based on your `Dockerfile`. This is especially important if you have made changes to the Dockerfile.

3. **Accessing the Application**: Once the containers are running, you can access your Django application at `http://localhost:8000`. The application will be running in a Docker container, and any changes made to your Django files will be reflected in real-time.

### Stopping the Application

To stop and remove the containers, networks, and volumes created by `docker-compose up`, you can use the following command in the same directory:

```bash
docker-compose down
