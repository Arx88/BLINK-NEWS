#!/bin/bash
echo "Enviando solicitud para regenerar Blinks de la página principal..."
curl "http://localhost:5000/api/news?refresh=true"
echo -e "\n\nSolicitud de regeneración enviada. Monitorea los logs del backend."
echo "Para generar una nota de un tema específico, modifica y usa este comando:"
echo 'curl -X POST -H "Content-Type: application/json" -d '\''{"topic": "Tu Tema Aqui"}'\'' http://localhost:5000/api/topic_search'
