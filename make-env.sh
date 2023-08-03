#!/bin/bash

cat > ./app/.env <<EOF

HOST=http://127.0.0.1
PORT=6000

DB_NAME=social_network
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=postgres:5432

JWT_KEY = 78hdls&02kihal9ehchwGH8skAHhr0KSHdv'kq19316&@9dcd9&)@
JWT_REFRESH_KEY = hdfk(!8dhcsdfk-e+sfle;vdf9kdjdfhlaey%@138fhDGA;s90

HUNTER_IO_API_KEY = 5c9280db861d8d1d9e28985cf0cbe6123f2aa165
HUNTER_IO_API_HOST = https://api.hunter.io/v2
HUNTER_IO_API_VERIFIER = /email-verifier?email={email}&api_key={api_key}

EOF
