# Expense Tracker MCP Server

A FastMCP-based expense tracker server with MongoDB storage.

## Features

- Add expenses with date, amount, category, subcategory, and note
- List expenses by inclusive date range
- Summarize totals by category (optionally filtered to one category)
- Expose categories as an MCP resource at `expense://categories`

## Tech Stack

- Python 3.11+
- [FastMCP](https://github.com/jlowin/fastmcp)
- MongoDB via `pymongo`

## Project Structure

- `main.py`: MCP server and tool/resource definitions
- `categories.json`: Category and subcategory data served as an MCP resource
- `pyproject.toml`: Project metadata and dependencies

## Prerequisites

- Python 3.11 or newer
- A running MongoDB instance (local or remote)

## Installation

### Option 1: Using uv (recommended)

```bash
uv sync
```

### Option 2: Using pip

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install fastmcp pymongo
```

## Configuration

Set these optional environment variables:

- `MONGODB_URI` (default: `mongodb://localhost:27017`)
- `MONGODB_DB` (default: `expense_tracker`)
- `MONGODB_COLLECTION` (default: `expenses`)

PowerShell example:

```powershell
$env:MONGODB_URI = "mongodb://localhost:27017"
$env:MONGODB_DB = "expense_tracker"
$env:MONGODB_COLLECTION = "expenses"
```

## Run the MCP Server

```bash
uv run fastmcp run main.py
```

## Install for Claude Desktop

```bash
uv run fastmcp install claude-desktop main.py
```

## MCP API

### Tool: `add_expense`

Inputs:

- `date` (string)
- `amount` (number/string)
- `category` (string)
- `subcategory` (string, optional)
- `note` (string, optional)

Returns:

- `{ "status": "ok", "id": "<mongo_object_id>" }`

### Tool: `list_expenses`

Inputs:

- `start_date` (string)
- `end_date` (string)

Returns an array of expense objects sorted by date and insertion order.

### Tool: `summarize`

Inputs:

- `start_date` (string)
- `end_date` (string)
- `category` (string, optional)

Returns category-wise totals:

- `[{ "category": "food", "total_amount": 1234.56 }, ...]`

### Resource: `expense://categories`

Returns the raw JSON from `categories.json`.

## Notes

- Dates are stored and compared as strings, so use a sortable format like `YYYY-MM-DD`.
- The server creates MongoDB indexes for faster date and category/date queries at startup.
