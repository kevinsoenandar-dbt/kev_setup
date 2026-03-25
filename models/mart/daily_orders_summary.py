def model(dbt, session):
    from snowflake.snowpark.functions import col, lit, sum as sum_, to_date, when

    order_items = dbt.ref('fct_order_items', v=2)

    daily = (
        order_items
        .with_column('order_date', to_date(col('ordered_at')))
        .group_by(col('order_date'))
        .agg(
            sum_(when(col('is_drink_item'), col('product_price')).otherwise(lit(0))).alias('drink_order_amount'),
            sum_(when(col('is_food_item'), col('product_price')).otherwise(lit(0))).alias('food_order_amount'),
        )
        .select('order_date', 'drink_order_amount', 'food_order_amount')
        .orderBy('order_date')
    )

    return daily
