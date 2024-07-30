from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from docker import DockerClient

from helpers.prefix_helper import PrefixMiddleware
from models.container_stat import db, ContainerStat, init_db
from blueprints.containers import bp as containers_bp, calculate_cpu_percent
from helpers.logging_helper import setup_logging
import logging
import os

setup_logging()
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///simple.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix=os.getenv('APP_PATH', '/'))

db.init_app(app)

docker_client = DockerClient(base_url='unix://var/run/docker.sock')

def collect_stats():
    with app.app_context():
        logger.info('Collecting container stats')
        containers = docker_client.containers.list(all=True)
        for container in containers:
            if container.status == 'running':
                stats = container.stats(stream=False)
                cpu_percentage = calculate_cpu_percent(stats)
                memory_usage = stats['memory_stats']['usage'] / (1024 * 1024)  # Convert to MB
                stat = ContainerStat(
                    container_id=container.id,
                    timestamp=datetime.utcnow(),
                    cpu_percentage=cpu_percentage,
                    memory_usage=memory_usage
                )
                db.session.add(stat)
                logger.info(f'Stats collected for container {container.id}')
        db.session.commit()
        logger.info('Stats collection completed')

def delete_old_stats():
    with app.app_context():
        logger.info('Deleting old stats')
        one_week_ago = datetime.utcnow() - timedelta(days=1)
        deleted_count = ContainerStat.query.filter(ContainerStat.timestamp < one_week_ago).delete()
        db.session.commit()
        logger.info(f'Deleted {deleted_count} old stats')

scheduler = BackgroundScheduler()
scheduler.add_job(collect_stats, 'interval', minutes=1)
scheduler.add_job(delete_old_stats, 'interval', days=1)
scheduler.start()
logger.info('Scheduler started')

@app.route('/')
def index():
    logger.info('Rendering index page')
    return render_template('index.html')

@app.route('/containers/<container_id>')
def container_detail(container_id):
    logger.info(f'Rendering detail page for container {container_id}')
    return render_template('detail.html', container_id=container_id)

app.register_blueprint(containers_bp, url_prefix='/api')

if __name__ == "__main__":
    with app.app_context():
        init_db(app)
    app.run(debug=True)
    logger.info('Application started')
