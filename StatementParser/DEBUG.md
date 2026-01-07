
If you wanto connect to service outside docker
> wsl
$ hostname -I
$ 192.168.153.156


┌─────────────────────────────────────────────────────────┐
│                    Windows Host                         │
│                   192.168.0.152                         │
│                                                         │
│  ┌─────────────────┐      ┌────────────────────────┐    │
│  │  Docker Desktop │      │         WSL            │    │
│  │                 │      │    192.168.144.x       │    │
│  │  ┌───────────┐  │      │                        │    │
│  │  │   n8n     │  │  ?   │  ┌─────────────────┐   │    │
│  │  │ container │◄─┼──────┼──│ FastAPI :8000   │   │    │
│  │  └───────────┘  │      │  └─────────────────┘   │    │
│  └─────────────────┘      └────────────────────────┘    │
└─────────────────────────────────────────────────────────┘

for pg admin also the above ip instead of docker container name



# windows & linux
> sed -i 's/\r$//' .env


ls -ld StatementParser/temp/statements

docker exec -it statement_parser_api ls -l /app/temp/statements
docker exec -it statement_parser_worker ls -l /app/temp/statements
