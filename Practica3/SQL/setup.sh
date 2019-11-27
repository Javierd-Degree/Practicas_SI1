dropdb -U alumnodb si1
createdb -U alumnodb si1
echo "======================================"
echo "Cargamos la base de datos"
gunzip -c dump_v1.3.sql.gz | psql -U alumnodb si1

echo "======================================"
echo "Actualizamos la base de datos"
psql -U alumnodb si1 -f actualiza.sql

echo "======================================"
echo "Ejecutamos setPrice"
psql -U alumnodb si1 -f setPrice.sql

echo "======================================"
echo "Instalamos y llamamos a setOrderAmount"
psql -U alumnodb si1 -f setOrderAmount.sql
# Ejecutamos setOrderAmount
psql -U alumnodb si1 -c "SELECT * FROM setOrderAmount()"

echo "======================================"
echo "Instalamos getTopVentas"
psql -U alumnodb si1 -f getTopVentas.sql

echo "======================================"
echo "Instalamos getTopMonths"
psql -U alumnodb si1 -f getTopMonths.sql

echo "======================================"
echo "Instalamos el trigger updOrders"
psql -U alumnodb si1 -f updOrders.sql

echo "======================================"
echo "Instalamos el trigger updInventory"
psql -U alumnodb si1 -f updInventory.sql
