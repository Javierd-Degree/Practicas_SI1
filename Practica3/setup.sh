dropdb -U alumnodb si1
createdb -U alumnodb si1
gunzip -c dump_v1.3.sql.gz | psql -U alumnodb si1
