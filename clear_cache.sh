#!/bin/bash
echo "Borrando contenido generado..."
BASE_DATA_DIR="news-blink-backend/src/data"
DIRECTORIES_TO_CLEAN=("blinks" "articles" "superior_notes" "topic_searches" "raw_news")

for dir in "${DIRECTORIES_TO_CLEAN[@]}"; do
    TARGET_PATH="$BASE_DATA_DIR/$dir"
    if [ -d "$TARGET_PATH" ]; then
        echo "Limpiando $TARGET_PATH/..."
        find "$TARGET_PATH" -type f -name "*.json" -delete
    fi
done
echo "Limpieza completada."
