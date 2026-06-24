with

source as (

    select * from {{ source('jaffle_shop', 'raw_customers') }}

)

select

    ----------  ids
    id as customer_id,

    ---------- text
    name as customer_name

from source