# SimpleDockerManager

SimpleDockerManager is a lightweight, web-based application for managing Docker containers, inspired by Dozzle. It allows you to monitor and manage Docker containers with ease, providing real-time insights into container performance metrics such as CPU and memory usage.

## Screenshots
[![Screenshot-2024-07-30-124054.png](https://i.postimg.cc/432VXsqt/Screenshot-2024-07-30-124054.png)](https://postimg.cc/B8DXg9qQ)
[![Screenshot-2024-07-30-124157.png](https://i.postimg.cc/CxYjNvbZ/Screenshot-2024-07-30-124157.png)](https://postimg.cc/bsCDY9C8)

## Features

- List Docker containers grouped by Docker Compose projects
- View detailed container information including CPU and memory usage
- Real-time log streaming
- Start and stop containers
- Network details
- Historical performance data visualization

## Prerequisites

- Docker
- Docker Compose

## Installation

### Using Docker

1. **Pull the Docker image:**
   ```sh
   docker pull rsatdev/simpledockermanager
   ```

2. **Run the Docker container with Docker socket:**
   ```sh
   docker run -d -p 5000:5000 -v /var/run/docker.sock:/var/run/docker.sock rsatdev/simpledockermanager
   ```

### Manual Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/rsatdev/simpledockermanager.git
   cd simpledockermanager
   ```

2. **Create a virtual environment and activate it:**
   ```sh
   python -m venv venv
   source venv/bin/activate 
   ```

3. **Install the dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```sh
   flask run
   ```

## Usage

1. Access the application in your web browser at `http://localhost:5000`.
2. The main dashboard displays a list of Docker containers.
3. Click on a container name to view detailed information and performance metrics.
4. Use the buttons to start or stop containers.

## License

This project is licensed under the MIT License.