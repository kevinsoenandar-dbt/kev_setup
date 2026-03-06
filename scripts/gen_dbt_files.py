#!/usr/bin/env python

import subprocess
import json
import os
import logging
import errno
import yaml
import argparse


# TODO add ability to define alias for sources

STAGING_FOLDER = "staging" # change this if the "staging" folder equivalent is different
SOURCE_FILE_NAME = "sources.yml"

logging.basicConfig(level=logging.INFO)


# Setup of the different commands and their arguments
parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(
    title="subcommands", description="valid subcommands", dest="command"
)
generate_source = subparsers.add_parser("generate_source")

generate_source.add_argument("database_name")
generate_source.add_argument("schema_name")
generate_source.add_argument("--overwrite", action="store_true")
generate_source.add_argument("--name", type=str, help="Name for the source (default: schema_name)")
generate_source.add_argument("--include-data-types", action="store_true")
generate_source.add_argument("--table-names", type=str, help="Comma-separated list of table names (e.g. raw_orders,raw_customers)")
generate_source.add_argument("--include-descriptions", action="store_true")
generate_source.add_argument("--generate-columns", action="store_true")
generate_source.add_argument("--metadata-schema", type=str, help="Schema for metadata tables (default: schema_name)")
generate_source.add_argument("--metadata-database", type=str, help="Database for metadata tables (default: database_name)")

args = parser.parse_args()

if args.name is None:
    args.name = args.schema_name


def generate_yml_sources(macro_args):
    """Run dbt update_source_metadata with the given args. Pass None for params to use macro defaults."""
    result = subprocess.run(
        [
            "dbt",
            "run-operation",
            "update_source_metadata",
            "--args",
            json.dumps(macro_args),
            "--quiet",
        ],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    )

    # dbt may send "Created invocation id" to stdout and macro output (YAML) to stderr
    combined = (result.stdout or "") + (result.stderr or "")
    # Extract YAML content (starts with "version: 2"); ignore invocation/status lines
    if "version: 2" in combined:
        outp = combined[combined.index("version: 2"):].strip()
    else:
        outp = combined.strip()

    return outp


def save_yml_sources(macro_args, overwrite=False):
    schema_name = macro_args["schema_name"]
    database_name = macro_args["database_name"]
    filepath = f"./models/{STAGING_FOLDER}/{schema_name}/_{schema_name}_{SOURCE_FILE_NAME}"

    if os.path.exists(filepath):
        if not overwrite:
            logging.info(
                f"The file {schema_name}/{SOURCE_FILE_NAME} already exists and was kept unchanged"
            )
            return
        else:
            logging.warning(
                f"The file {schema_name}/{SOURCE_FILE_NAME} already existed and will be overwritten"
            )

    yml_data = generate_yml_sources(macro_args)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "w") as f:
        f.write(yml_data)
    logging.info(f"The file {schema_name}/_{schema_name}_{SOURCE_FILE_NAME} has been written to:")
    logging.info(f"{filepath}")


def read_yml_sources(folder):
    """Read source definitions from models/staging/{folder}/_sources.yml.
    Use database_name for generate_source_staging, source_name for generate_staging."""
    yml_file_path = f"./models/{STAGING_FOLDER}/{folder}/{SOURCE_FILE_NAME}"
    if not os.path.exists(yml_file_path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), yml_file_path)

    source_tables_list = []

    with open(yml_file_path) as yml_file:
        sources_list = yaml.load(yml_file, Loader=yaml.FullLoader)

    for source_table in sources_list["sources"][0]["tables"]:
        source_tables_list.append(
            {
                "source_name": sources_list["sources"][0]["name"],
                "table_name": source_table["name"],
            }
        )

    logging.info(
        f"Read {len(source_tables_list)} tables from {folder}/{SOURCE_FILE_NAME}"
    )
    return source_tables_list


if __name__ == "__main__":

    table_names = None
    if hasattr(args, "table_names") and args.table_names:
        table_names = [t.strip() for t in args.table_names.split(",")]
    macro_args = {
        "schema_name": args.schema_name,
        "database_name": args.database_name,
        "table_names": table_names,
        "name": getattr(args, "name", args.schema_name),
        "include_descriptions": getattr(args, "include_descriptions", False),
        "generate_columns": getattr(args, "generate_columns", False),
        "include_data_types": getattr(args, "include_data_types", False),
        "metadata_schema": getattr(args, "metadata_schema", None),
        "metadata_database": getattr(args, "metadata_database", None)
    }
    save_yml_sources(macro_args, overwrite=args.overwrite)