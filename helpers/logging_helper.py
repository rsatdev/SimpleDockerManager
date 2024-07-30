from logging.config import dictConfig

def setup_logging():
    logging_config = dict(
        version=1,
        formatters={
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            },
        },
        handlers={
            'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'default'
            },
            #'file': {
            #    'class': 'logging.FileHandler',
            #    'filename': 'app.log',
            #    'formatter': 'default'
            #},
        },
        root={
            'level': 'INFO',
            #'handlers': ['wsgi', 'file']
            'handlers': ['wsgi']
        }
    )
    dictConfig(logging_config)
