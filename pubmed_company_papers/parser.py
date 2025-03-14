"""
Module for parsing PubMed XML data and identifying company affiliations.
"""
from typing import Dict, List, Optional, Tuple, Set, Any
import re
import logging
from xml.etree import ElementTree as ET
import pandas as pd

# Configure logging
logger = logging.getLogger(__name__)

# Keywords indicating academic institutions
ACADEMIC_KEYWORDS = {
    "university", "college", "institute", "school", "academy", "facultad", "universität", 
    "université", "università", "academia", "medical center", "hospital", "clinic", 
    "medical school", "faculty", "department", "universitat"
}

# Keywords indicating pharmaceutical or biotech companies
COMPANY_KEYWORDS = {
    "pharma", "therapeutics", "biotech", "bioscience", "biopharma", "laboratories",
    "labs", "inc", "llc", "ltd", "limited", "corp", "plc", "gmbh", "co", "ag", 
    "biomed", "genomics", "pharmaceuticals"
}

def is_company_affiliation(affiliation: str) -> bool:
    """
    Determine if an affiliation is from a pharmaceutical or biotech company.
    
    Args:
        affiliation: The affiliation string to check
        
    Returns:
        True if the affiliation appears to be from a company, False otherwise
    """
    if not affiliation:
        return False
        
    affiliation_lower = affiliation.lower()
    
    # Check if this looks like an academic institution
    if any(keyword in affiliation_lower for keyword in ACADEMIC_KEYWORDS):
        return False
        
    # Check if this looks like a company
    return any(keyword in affiliation_lower for keyword in COMPANY_KEYWORDS)

def extract_company_name(affiliation: str) -> str:
    """
    Extract the company name from an affiliation string.
    
    Args:
        affiliation: The affiliation string
        
    Returns:
        The extracted company name, or the full affiliation if extraction fails
    """
    # Try to extract company name - this is a simple heuristic and may need refinement
    # First, try to find company patterns like "X, Inc." or "X Ltd."
    company_pattern = re.compile(r'([A-Za-z0-9\s\-]+)(?:\s+(?:Inc|LLC|Ltd|Limited|Corp|Corporation|GmbH|AG|Co|SA|BV|Pty)\.?)')
    match = company_pattern.search(affiliation)
    
    if match:
        return match.group(1).strip()
    
    # If that fails, just return the first part of the affiliation
    parts = affiliation.split(',')
    if parts:
        return parts[0].strip()
    
    return affiliation

def extract_email(text: str) -> Optional[str]:
    """
    Extract an email address from text.
    
    Args:
        text: Text that may contain an email address
        
    Returns:
        The extracted email address, or None if no email is found
    """
    if not text:
        return None
        
    email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    match = email_pattern.search(text)
    
    return match.group(0) if match else None

def parse_publication_date(date_elem: Optional[ET.Element]) -> str:
    """
    Parse a publication date element into a string.
    
    Args:
        date_elem: The XML element containing date information
        
    Returns:
        A formatted date string (YYYY-MM-DD), or an empty string if parsing fails
    """
    if date_elem is None:
        return ""
    
    year = date_elem.findtext("Year") or ""
    month = date_elem.findtext("Month") or ""
    day = date_elem.findtext("Day") or ""
    
    if not year:
        return ""
    
    if month.isdigit():
        month_int = int(month)
        if 1 <= month_int <= 12:
            month = month.zfill(2)
        else:
            month = "01"  # Default to January for invalid months
    else:
        # Try to convert month names to numbers
        month_dict = {
            "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
            "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12"
        }
        month_lower = month.lower()[:3]
        month = month_dict.get(month_lower, "01")
    
    if day.isdigit():
        day = day.zfill(2)
    else:
        day = "01"  # Default to first day of month
    
    return f"{year}-{month}-{day}"

def parse_papers(xml_elements: List[ET.Element]) -> List[Dict[str, Any]]:
    """
    Parse PubMed XML data into structured paper information.
    Filter for papers with at least one author from a pharmaceutical or biotech company.
    
    Args:
        xml_elements: List of XML elements containing paper data
        
    Returns:
        List of dictionaries with structured paper information
    """
    papers = []
    
    for xml_root in xml_elements:
        for article_elem in xml_root.findall(".//PubmedArticle"):
            paper_data = {}
            
            # Extract PubMed ID
            pmid_elem = article_elem.find(".//PMID")
            if pmid_elem is None:
                continue
            paper_data["PubmedID"] = pmid_elem.text
            
            # Extract title
            title_elem = article_elem.find(".//ArticleTitle")
            paper_data["Title"] = title_elem.text if title_elem is not None else ""
            
            # Extract publication date
            pub_date_elem = article_elem.find(".//PubDate")
            paper_data["Publication Date"] = parse_publication_date(pub_date_elem)
            
            # Process authors
            author_elems = article_elem.findall(".//Author")
            non_academic_authors = []
            company_affiliations = set()
            corresponding_email = None
            
            for author_elem in author_elems:
                # Extract author name
                last_name = author_elem.findtext("LastName") or ""
                fore_name = author_elem.findtext("ForeName") or ""
                author_name = f"{last_name}, {fore_name}".strip(", ")
                
                # Extract affiliations
                affiliations = []
                for aff_elem in author_elem.findall(".//Affiliation"):
                    if aff_elem.text:
                        affiliations.append(aff_elem.text)
                
                # Check if corresponding author
                is_corresponding = False
                for aut_note_elem in author_elem.findall(".//ELocationID[@EIdType='email']"):
                    if aut_note_elem.text:
                        is_corresponding = True
                        corresponding_email = aut_note_elem.text
                
                # If no explicit email in XML, try to extract from affiliation text
                if not corresponding_email and is_corresponding:
                    for aff in affiliations:
                        email = extract_email(aff)
                        if email:
                            corresponding_email = email
                            break
                
                # Check if author is from a company
                for affiliation in affiliations:
                    if is_company_affiliation(affiliation):
                        non_academic_authors.append(author_name)
                        company_name = extract_company_name(affiliation)
                        company_affiliations.add(company_name)
                        break
            
            # Only include papers with at least one non-academic author
            if non_academic_authors:
                paper_data["Non-academic Author(s)"] = "; ".join(non_academic_authors)
                paper_data["Company Affiliation(s)"] = "; ".join(company_affiliations)
                paper_data["Corresponding Author Email"] = corresponding_email or ""
                papers.append(paper_data)
    
    return papers

def papers_to_dataframe(papers: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert paper data to a pandas DataFrame.
    
    Args:
        papers: List of dictionaries with paper information
        
    Returns:
        DataFrame with paper information
    """
    if not papers:
        # Return empty DataFrame with the required columns
        return pd.DataFrame(columns=[
            "PubmedID", "Title", "Publication Date", 
            "Non-academic Author(s)", "Company Affiliation(s)", 
            "Corresponding Author Email"
        ])
    
    return pd.DataFrame(papers)