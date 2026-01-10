

docker-compose up statement-parser-api -d

docker-compose up --build statement-parser-api -d
docker-compose up --build statement-parser-worker -d
docker-compose up --build statement-parser-beat -d

docker-compose restart statement-parser-api -d
docker-compose restart statement-parser-worker -d
docker-compose restart statement-parser-beatpi -d
