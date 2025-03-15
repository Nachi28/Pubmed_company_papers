# PubMed Company Papers

A Python tool to fetch research papers based on a query and identify those with authors affiliated with pharmaceutical or biotech companies.

## Features

- Search PubMed using their full query syntax
- Identify papers with at least one author from a pharmaceutical or biotech company
- Output results as CSV with key information
- Command-line interface with options for debugging and file output

## Installation

### Prerequisites

- Python 3.9 or higher
- [Poetry](https://python-poetry.org/) for dependency management

### Install from GitHub

```bash
# Clone the repository
git clone https://github.com/yourusername/pubmed-company-papers.git
cd pubmed-company-papers

# Install dependencies using Poetry
poetry install
```

## Usage

After installation, you can use the tool via the command line:

```bash
# Basic usage
poetry run get-papers-list "cancer immunotherapy"

# Save results to a CSV file
poetry run get-papers-list "cancer immunotherapy" --file results.csv

# Enable debug output
poetry run get-papers-list "cancer immunotherapy" --debug

# Process more results
poetry run get-papers-list "cancer immunotherapy" --max-results 200
```

### Command-line Options

- `QUERY`: PubMed search query (required positional argument)
- `-d, --debug`: Print debug information during execution
- `-f, --file`: Specify the filename to save the results (CSV format)
- `-m, --max-results`: Maximum number of results to process (default: 100)
- `-h, --help`: Show help message

### Example

```bash
poetry run get-papers-list "CRISPR[Title] AND 2023[PDAT]" --file crispr_2023.csv
```

This will search for papers with "CRISPR" in the title published in 2023, identify those with authors affiliated with pharmaceutical or biotech companies, and save the results to `crispr_2023.csv`.

## Code Organization

The package is organized as follows:

```
pubmed_company_papers/
├── pubmed_company_papers/
│   ├── __init__.py       # Package initialization
│   ├── api.py            # PubMed API client
│   ├── parser.py         # XML parsing and company affiliation detection
│   ├── main.py           # Core functionality
│   └── cli.py            # Command-line interface
├── pyproject.toml        # Poetry configuration
└── README.md             # Documentation
```

- `api.py`: Contains the `PubMedAPI` class for interacting with the PubMed API
- `parser.py`: Functions for parsing XML data and identifying company affiliations
- `main.py`: Core functionality for fetching and processing papers
- `cli.py`: Command-line interface using Click

## Using as a Module

You can also use the package as a module in your own Python code:

```python
from pubmed_company_papers import get_papers_with_company_authors
import pandas as pd

# Fetch papers
df = get_papers_with_company_authors("cancer therapy", max_results=50)

# Process the results
print(f"Found {len(df)} papers with company authors")
print(df.head())
```

## Development

### Running Tests

```bash
poetry run pytest
```

### Type Checking

```bash
poetry run mypy pubmed_company_papers
```

### Code Formatting

```bash
poetry run black pubmed_company_papers
poetry run isort pubmed_company_papers
```

## Tools and Libraries Used

- [Poetry](https://python-poetry.org/): Dependency management and packaging
- [Requests](https://requests.readthedocs.io/): HTTP library for API calls
- [Pandas](https://pandas.pydata.org/): Data manipulation and CSV generation
- [Click](https://click.palletsprojects.com/): Command-line interface creation
- [BioPython](https://biopython.org/): Used for parsing PubMed data
- [mypy](https://mypy.readthedocs.io/): Static type checking
- [Black](https://black.readthedocs.io/): Code formatting
