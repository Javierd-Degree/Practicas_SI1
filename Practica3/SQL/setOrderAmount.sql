CREATE OR REPLACE FUNCTION setOrderAmount()
    RETURNS VOID
AS $$
    DECLARE
    BEGIN
      UPDATE orders o SET netamount=p.price FROM setOrderAmountView p WHERE o.orderid=p.orderid;
      UPDATE orders o SET totalamount=ROUND((o.netamount+o.netamount*o.tax/100)::numeric, 2);
    END;
$$ LANGUAGE plpgsql;
