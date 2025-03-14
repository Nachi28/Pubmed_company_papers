"""
Command-line interface for the PubMed company papers tool.
"""
import sys
import logging
from typing import Optional
import click
from .main import get_papers_with_company_authors

@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('query')
@click.option('-d', '--debug', is_flag=True, help='Print debug information during execution.')
@click.option('-f', '--file', type=str, help='Specify the filename to save the results. If not provided, print to console.')
@click.option('-m', '--max-results', type=int, default=100, help='Maximum number of results to process. Default is 100.')
def main(query: str, debug: bool = False, file: Optional[str] = None, max_results: int = 100) -> None:
    """
    Fetch research papers based on a query and identify those with at least one author
    affiliated with a pharmaceutical or biotech company.
    
    QUERY: A search query following PubMed's syntax.
    
    Example:
        get-papers-list "cancer immunotherapy" --file results.csv
    """
    try:
        # Get papers with company authors
        df = get_papers_with_company_authors(query, max_results=max_results, debug=debug)
        
        if df.empty:
            click.echo("No papers found with authors from pharmaceutical or biotech companies.")
            return
        
        # Output results
        if file:
            df.to_csv(file, index=False)
            click.echo(f"Results saved to {file}")
        else:
            # Print to console
            click.echo(df.to_string(index=False))
            
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()