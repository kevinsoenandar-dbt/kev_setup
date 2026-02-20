# Kev's Personal Sandbox for all things Snowflake + dbt

## Update Sources Weekly

This workflow runs every Monday to regenerate dbt source YAML files from your data warehouse schema. If changes are detected, it automatically opens a PR.

### Setup

1. **Add GitHub Variables and Secrets** (Settings → Secrets and variables → Actions):
   - **Variables:** `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_DATABASE`, `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_SCHEMA`, `SNOWFLAKE_ROLE`
   - **Secrets:** `SNOWFLAKE_USERNAME`, `SNOWFLAKE_PASSWORD`

2. **profiles.yml** in the project root uses `env_var()` for these values—no secrets in code.

3. **Configure sources** in `.github/source-sync-config.yml`:
   - Add each database/schema pair you want to sync
   - Each source runs `generate_source` to update `_sources.yml`
   - Set the `generate_columns`, `include_descriptions` and `include_data_types` flags as `true` to ensure the query to pull the metadata gets run
      - Note that currently the data types being pulled is the actual data type from the warehouse metadata information as opposed to the manual metadata table. 

4. **Adjust dbt adapter** in the workflow if needed:
   - Default is `dbt-snowflake`
   - Change to `dbt-bigquery`, `dbt-databricks`, etc. in the "Install dbt" step

### Manual run

Trigger the workflow manually: Actions → Update Sources Weekly → Run workflow
