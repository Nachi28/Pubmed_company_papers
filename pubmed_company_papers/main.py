"""
Main module containing the core functionality to fetch and process papers.
"""
from typing import List, Dict, Optional, Any
import logging
import pandas as pd
from .api import PubMedAPI
from .parser import parse_papers, papers_to_dataframe

# Configure logging
logger = logging.getLogger(__name__)

def get_papers_with_company_authors(
    query: str, 
    max_results: int = 100,
    debug: bool = False
) -> pd.DataFrame:
    """
    Fetch papers matching the query and filter for those with authors 
    affiliated with pharmaceutical or biotech companies.
    
    Args:
        query: PubMed search query
        max_results: Maximum number of results to return after filtering
        debug: Whether to print debug information
        
    Returns:
        DataFrame containing the filtered papers
    """
    # Configure logging based on debug flag
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info(f"Starting search with query: {query}")
    
    # Initialize API client
    api = PubMedAPI()
    
    # Adaptive approach: start with batch size and increase if needed
    initial_batch_size = min(max_results * 3, 1000)  # Start with triple the requested size
    
    try:
        all_papers = []
        current_batch_size = initial_batch_size
        total_fetched = 0
        
        # Continue fetching until we have enough papers or exhausted options
        while len(all_papers) < max_results:
            # Calculate how many more papers we need
            papers_needed = max_results - len(all_papers)
            
            # Adjust batch size based on the filter rate from previous batches
            if all_papers and total_fetched > 0:
                # Calculate the filter rate (how many papers survive the filter)
                filter_rate = len(all_papers) / total_fetched
                # Adjust batch size based on the filter rate
                adjusted_batch_size = min(int(papers_needed / max(filter_rate, 0.01)), 1000)
                current_batch_size = max(adjusted_batch_size, 100)  # At least 100 papers
            
            logger.info(f"Fetching batch of {current_batch_size} papers (have {len(all_papers)} of {max_results} target)")
            
            # Search for papers with offset
            pmids = api.search(query, retmax=current_batch_size, retstart=total_fetched)
            
            if not pmids:
                logger.warning("No more papers found matching the query")
                break
                
            total_fetched += len(pmids)
            
            # Fetch paper details
            xml_results = api.batch_fetch_papers(pmids)
            
            # Parse papers and filter for company affiliations
            batch_papers = parse_papers(xml_results)
            
            # Add to our collection
            all_papers.extend(batch_papers)
            
            logger.info(f"After this batch: {len(all_papers)} papers with company affiliations out of {total_fetched} total fetched")
            
            # If we fetched a batch but got no company papers, adjust batch size
            if not batch_papers:
                current_batch_size = min(current_batch_size * 2, 1000)
            
            # If we've fetched a lot of papers but still don't have enough, we might need to stop
            if total_fetched >= 10000 and len(all_papers) < max_results:
                logger.warning(f"Stopping after fetching {total_fetched} papers, only found {len(all_papers)} with company affiliations")
                break
        
        # Trim to max_results if we have more
        if len(all_papers) > max_results:
            all_papers = all_papers[:max_results]
        
        logger.info(f"Final result: {len(all_papers)} papers with authors from companies out of {total_fetched} total papers fetched")
        
        # Convert to DataFrame
        df = papers_to_dataframe(all_papers)
        
        return df
        
    except Exception as e:
        logger.error(f"Error fetching papers: {str(e)}")
        raise