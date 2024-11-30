Hello Anna

## .env setup
root level .env (ask for deetails)

frontend level .env.local copy across from example.env

## run
`docker compose up -d`

## logs
`docker compose logs -f ${service name}`

## setup db 
`cd frontend`
`pnpm db:migrate`

