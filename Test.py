import logging
from pubmed_company_papers import get_papers_with_company_authors

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Example usage
query = "cancer immunotherapy"
df = get_papers_with_company_authors(query, max_results=100, debug=True)

if df.empty:
    print("No papers found with authors from pharmaceutical or biotech companies.")
else:
    print(f"Found {len(df)} papers with authors from companies:")
    print(df.to_string(index=False))