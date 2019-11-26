dropdb -U alumnodb si1
createdb -U alumnodb si1
gunzip -c dump_v1.3.sql.gz | psql -U alumnodb si1
psql -U alumnodb si1 -f actualiza.sql
psql -U alumnodb si1 -f setPrice.sql
psql -U alumnodb si1 -f setOrderAmount.sql
# Ejecutamos setOrderAmount
psql -U alumnodb si1 -c "SELECT * FROM setOrderAmount()"
psql -U alumnodb si1 -f getTopVentas.sql
psql -U alumnodb si1 -f getTopMonths.sql
psql -U alumnodb si1 -f updOrders.sql
psql -U alumnodb si1 -f updInventory.sql
