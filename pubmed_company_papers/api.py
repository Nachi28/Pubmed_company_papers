"""
Module for interacting with the PubMed API.
"""
from typing import Dict, List, Optional, Union, Any
import logging
import time
import requests
from urllib.parse import quote_plus
from xml.etree import ElementTree as ET

# Configure logging
logger = logging.getLogger(__name__)

class PubMedAPI:
    """Client for interacting with the PubMed API."""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    SEARCH_URL = f"{BASE_URL}esearch.fcgi"
    FETCH_URL = f"{BASE_URL}efetch.fcgi"
    SUMMARY_URL = f"{BASE_URL}esummary.fcgi"
    
    def __init__(self, email: str = "user@example.com", tool: str = "pubmed-company-papers"):
        """
        Initialize the PubMed API client.
        
        Args:
            email: Email to identify yourself to NCBI (recommended)
            tool: Name of your tool (recommended)
        """
        self.email = email
        self.tool = tool
        
    def search(self, query: str, retmax: int = 100, retstart: int = 0) -> List[str]:
        """
        Search PubMed for papers matching the query.
        
        Args:
            query: PubMed search query
            retmax: Maximum number of results to return
            retstart: Starting index for results (for pagination)
            
        Returns:
            List of PubMed IDs matching the query
        """
        params = {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": retmax,
            "retstart": retstart,
            "tool": self.tool,
            "email": self.email
        }
        
        logger.debug(f"Searching PubMed with query: {query}, start: {retstart}, max: {retmax}")
        response = requests.get(self.SEARCH_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        pmids = data.get("esearchresult", {}).get("idlist", [])
        logger.debug(f"Found {len(pmids)} papers matching the query (offset: {retstart})")
        
        return pmids
    
    def fetch_papers(self, pmids: List[str]) -> Optional[ET.Element]:
        """
        Fetch detailed information for the given PubMed IDs.
        
        Args:
            pmids: List of PubMed IDs to fetch
            
        Returns:
            XML Element containing the paper data
        """
        if not pmids:
            logger.warning("No PubMed IDs provided to fetch_papers")
            return None
            
        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
            "tool": self.tool,
            "email": self.email
        }
        
        logger.debug(f"Fetching details for {len(pmids)} papers")
        response = requests.get(self.FETCH_URL, params=params)
        response.raise_for_status()
        
        # Parse XML response
        xml_root = ET.fromstring(response.content)
        return xml_root
    
    def batch_fetch_papers(self, pmids: List[str], batch_size: int = 200) -> List[ET.Element]:
        """
        Fetch papers in batches to avoid overwhelming the API.
        
        Args:
            pmids: List of PubMed IDs to fetch
            batch_size: Number of papers to fetch in each batch
            
        Returns:
            List of XML Elements containing the paper data
        """
        results = []
        
        for i in range(0, len(pmids), batch_size):
            batch = pmids[i:i + batch_size]
            xml_result = self.fetch_papers(batch)
            if xml_result is not None:
                results.append(xml_result)
            # Be nice to the API
            time.sleep(0.5)
            
        return results