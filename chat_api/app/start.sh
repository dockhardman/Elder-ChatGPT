set -e

uvicorn app.main:app \
    --host=0.0.0.0 \
    --port=80 \
    --reload \
    --log-level=debug \
    --use-colors
