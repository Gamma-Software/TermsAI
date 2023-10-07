echo "Setting up virtual environment and installing dependencies"
virtualenv .venv
.venv/bin/python -m pip install -r requirements.txt

echo "Setting up database"
docker pull redis/redis-stack-server:latest
docker volume create redis-data
docker run --name terms_ai_redis -p "6379":"6379" -v redis-data:/data -d redis/redis-stack-server:latest