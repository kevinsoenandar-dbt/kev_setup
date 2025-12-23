with staging as (
    select * from {{ ref('stg_products') }}
)

select
    product_id,
    product_name, 
    product_type,
    product_description

from staging