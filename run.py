from gc import DEBUG_LEAK
from app import app
from config import FLASK_RUN_HOST, FLASK_RUN_PORT, FLASK_DEBUG_FLAG

if __name__ == '__main__':
    # Retrieve port (and host) from the application's configuration
    port = FLASK_RUN_PORT
    host = FLASK_RUN_HOST
    debug_flag = FLASK_DEBUG_FLAG

    app.run(host=host, port=port,debug=debug_flag)
