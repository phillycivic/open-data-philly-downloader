# open-data-philly-downloader

Download any table from Philadelphia's public Carto SQL API into a typed SQLite
database, with optional CSV output.

The downloader discovers table columns and types from Carto at runtime. It does
not validate rows against hand-written dataset models, so harmless upstream
schema variations do not abort an entire backup.

## Features

- Works with any table exposed by a compatible Carto SQL endpoint.
- Downloads large result sets in configurable pages.
- Retries rate limits and transient server errors.
- Supports whole-table, distinct-column, and date-period downloads.
- Derives SQLite column affinities from Carto field metadata.
- Preserves mixed upstream values using SQLite's permissive affinity rules.
- Optionally writes CSV files while streaming rows into SQLite.
- Adds `lat` and `lng` for tables containing `the_geom`.
- Creates requested SQLite indexes after loading completes.
- Orders pages by `cartodb_id`, falling back to `objectid`, when available.
- JSON-encodes nested values that SQLite cannot bind directly.

## Requirements

- Python 3.10.4 or newer
- [uv](https://docs.astral.sh/uv/) for the examples below

## Install

Install the released package as a command-line tool:

```bash
uv tool install open-data-philly-downloader
```

Then confirm the CLI is available:

```bash
odp-download --help
```

To run the latest commit without installing it permanently:

```bash
uvx --from git+https://github.com/phillycivic/open-data-philly-downloader \
  odp-download --help
```

## Download a complete table

```bash
odp-download table \
  --table business_licenses \
  --db-filepath open_data_philly.db \
  --index initialissuedate
```

The destination table is replaced when a download starts. Other tables in the
same SQLite database are left intact.

Add a Carto SQL filter with `--where`:

```bash
odp-download table \
  --table violations \
  --where "violationdate >= '2025-01-01'" \
  --db-filepath open_data_philly.db
```

`--where` and `--order-by` are SQL expressions sent to Carto. They should only
be populated with trusted input.

To write CSV and SQLite in the same download:

```bash
odp-download table \
  --table business_licenses \
  --csv-path business_licenses.csv
```

## Split a download by column

Splitting reduces the amount of upstream data handled by each query. Each split
is still paginated, so large split values are not truncated.

```bash
odp-download by-col \
  --table opa_properties_public \
  --csv-split-col zip_code \
  --db-filepath open_data_philly.db \
  --index zip_code
```

Add `--csv-dir csvs` to write one CSV file per split value.

## Split a download by date

Date downloads can be split by year, month, or day:

```bash
odp-download by-datetime \
  --table rtt_summary \
  --split-by recording_date year \
  --where "document_type IN ('DEED', 'DEED_SHERIFF')" \
  --db-filepath open_data_philly.db \
  --index recording_date
```

Add `--csv-dir csvs` to write one CSV file per time period.

## Common options

- `--db-filepath`: SQLite output path; defaults to `open_data_philly.db`.
- `--where`: optional Carto SQL filter.
- `--index`: SQLite column to index; repeat the option for multiple indexes.
- `--page-size`: rows requested per page; defaults to 25,000.
- `--endpoint`: alternate compatible Carto SQL API endpoint.
- `--add-lat-lng` / `--no-add-lat-lng`: control coordinate extraction.

Run `odp-download COMMAND --help` for the complete options for a command.

## SQLite types

Carto metadata is mapped to SQLite affinity as follows:

| Carto type | SQLite type |
| --- | --- |
| `boolean` | `INTEGER` |
| `number` | `NUMERIC` |
| `date` | `TEXT` |
| `string` | `TEXT` |
| `geometry` | `TEXT` |
| unknown | `NUMERIC` |

SQLite affinity is intentionally used instead of strict Python validation. For
example, if Carto reports a column as text but returns an integer in one row,
SQLite safely stores its text representation instead of failing the download.

## Development

Clone the repository and install the locked development environment:

```bash
uv sync --frozen
```

Run the checks:

```bash
uv run pytest
uv run ruff check .
uv build
```

CI runs the tests and linter on every push and pull request. Version tags invoke
the trusted-publishing workflow that builds and publishes the package to PyPI.
