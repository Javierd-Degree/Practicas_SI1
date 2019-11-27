CREATE OR REPLACE FUNCTION setOrderAmount()
    RETURNS VOID
AS $$
    DECLARE
    BEGIN
      UPDATE orders o SET netamount=p.price, totalamount=ROUND((p.price+p.price*o.tax/100)::numeric, 2)
      FROM setOrderAmountView p
      WHERE o.orderid=p.orderid;
    END;
$$ LANGUAGE plpgsql;
