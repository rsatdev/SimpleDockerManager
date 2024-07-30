from flask import Blueprint, jsonify, request, Response, stream_with_context
from docker import DockerClient, errors
from datetime import datetime, timedelta
from models.container_stat import ContainerStat
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('containers', __name__)
docker_client = DockerClient(base_url='unix://var/run/docker.sock')


def calculate_cpu_percent(stats):
    cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
    system_cpu_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
    cpu_percent = (cpu_delta / system_cpu_delta) * len(stats['cpu_stats']['cpu_usage']['percpu_usage']) * 100.0
    return cpu_percent


def get_docker_data():
    logger.info('Fetching Docker container data')
    containers = docker_client.containers.list(all=True)
    projects = {}

    for container in containers:
        project_name = container.labels.get('com.docker.compose.project', 'default')
        stats = container.stats(stream=False)
        created = datetime.strptime(container.attrs['Created'].split(".")[0], '%Y-%m-%dT%H:%M:%S')
        cpu_percentage = calculate_cpu_percent(stats) if container.status == 'running' else 0
        mem_usage = stats['memory_stats']['usage'] if container.status == 'running' else 0
        ports = container.attrs['NetworkSettings']['Ports']
        environment = container.attrs['Config']['Env']

        container_info = {
            "id": container.id,
            "name": container.name,
            "status": container.status,
            "image": container.image.tags,
            "created": created.strftime('%Y-%m-%d %H:%M:%S'),
            "cpu_percentage": cpu_percentage,
            "memory_usage": mem_usage,
            "ports": ports,
            "environment": environment,
            "memory_limit": stats['memory_stats']['limit'] if container.status == 'running' else 0
        }

        if project_name not in projects:
            projects[project_name] = []
        projects[project_name].append(container_info)

    logger.info('Docker container data fetched successfully')
    return projects


@bp.route('/containers', methods=['GET'])
def list_containers():
    logger.info('Listing all containers')
    data = get_docker_data()
    return jsonify(data)


@bp.route('/containers/<container_id>', methods=['GET'])
def container_detail(container_id):
    try:
        logger.info(f'Fetching details for container {container_id}')
        container = docker_client.containers.get(container_id)
        stats = container.stats(stream=False)
        created = datetime.strptime(container.attrs['Created'].split(".")[0], '%Y-%m-%dT%H:%M:%S')
        ports = container.attrs['NetworkSettings']['Ports']
        environment = container.attrs['Config']['Env']

        container_info = {
            "id": container.id,
            "name": container.name,
            "status": container.status,
            "image": container.image.tags,
            "created": created.strftime('%Y-%m-%d %H:%M:%S'),
            "logs": container.logs().decode('utf-8'),
            "cpu_percentage": calculate_cpu_percent(stats) if container.status == 'running' else 0,
            "memory_usage": stats['memory_stats']['usage'] if container.status == 'running' else 0,
            "ports": ports,
            "environment": environment
        }
        logger.info(f'Details fetched for container {container_id}')
        return jsonify(container_info)
    except errors.NotFound:
        logger.error(f'Container {container_id} not found')
        return jsonify({"error": "Container not found"}), 404


@bp.route('/containers/<container_id>/start', methods=['POST'])
def start_container(container_id):
    try:
        logger.info(f'Starting container {container_id}')
        container = docker_client.containers.get(container_id)
        container.start()
        logger.info(f'Container {container_id} started')
        return jsonify({"status": "started"})
    except errors.NotFound:
        logger.error(f'Container {container_id} not found')
        return jsonify({"error": "Container not found"}), 404


@bp.route('/containers/<container_id>/stop', methods=['POST'])
def stop_container(container_id):
    try:
        logger.info(f'Stopping container {container_id}')
        container = docker_client.containers.get(container_id)
        container.stop()
        logger.info(f'Container {container_id} stopped')
        return jsonify({"status": "stopped"})
    except errors.NotFound:
        logger.error(f'Container {container_id} not found')
        return jsonify({"error": "Container not found"}), 404


@bp.route('/containers/<container_id>/logs', methods=['GET'])
def container_logs(container_id):
    try:
        logger.info(f'Fetching logs for container {container_id}')
        container = docker_client.containers.get(container_id)
        log_stream = container.logs(stream=True)
        logger.info(f'Logs fetched for container {container_id}')
        return Response(stream_with_context(log_stream), content_type='text/plain')
    except errors.NotFound:
        logger.error(f'Container {container_id} not found')
        return jsonify({"error": "Container not found"}), 404


@bp.route('/containers/<container_id>/stats', methods=['GET'])
def container_stats(container_id):
    try:
        logger.info(f'Fetching stats for container {container_id}')

        time_range = request.args.get('time_range', '1h')
        time_deltas = {
            '30m': timedelta(minutes=30),
            '1h': timedelta(hours=1),
            '2h': timedelta(hours=2),
            '3h': timedelta(hours=3),
            '6h': timedelta(hours=6),
            '12h': timedelta(hours=12),
            '1d': timedelta(days=1)
        }

        if time_range not in time_deltas:
            return jsonify({"error": "Invalid time range"}), 400

        start_time = datetime.utcnow() - time_deltas[time_range]

        stats = ContainerStat.query.filter_by(container_id=container_id).filter(
            ContainerStat.timestamp >= start_time).order_by(ContainerStat.timestamp.asc()).all()

        timestamps = [stat.timestamp.strftime('%Y-%m-%d %H:%M:%S') for stat in stats]
        cpu_usage = [stat.cpu_percentage for stat in stats]
        memory_usage = [stat.memory_usage for stat in stats]

        return jsonify({
            "timestamps": timestamps,
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage
        })
    except errors.NotFound:
        logger.error(f'Container {container_id} not found')
        return jsonify({"error": "Container not found"}), 404