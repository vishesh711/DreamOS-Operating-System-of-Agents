"""
Web Browser tool for DreamOS
Uses Playwright for web browsing and information retrieval
"""
import os
import json
import time
from typing import Dict, Any, Optional, List
import asyncio
from pathlib import Path

try:
    from playwright.async_api import async_playwright, Page, Browser
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

from ..utils.logging_utils import get_logger

# Initialize logger
logger = get_logger("web_browser")

class WebBrowserTool:
    """Web browser tool for searching and retrieving information from the web."""
    
    def __init__(self):
        """Initialize the web browser tool."""
        self.name = "web_browser"
        self.description = "Searches the web and retrieves information"
        
        # Check if Playwright is available
        if not PLAYWRIGHT_AVAILABLE:
            logger.warning("Playwright not available. Please install with: pip install playwright")
            logger.warning("After installation, run: playwright install")
        
        # Defaults
        self.timeout = 30000  # milliseconds
        self.max_results = 5
        self.browser = None
        self.page = None
    
    async def _setup_browser(self) -> None:
        """Set up the browser instance."""
        logger.debug("Setting up browser instance")
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()
        await self.page.set_viewport_size({"width": 1280, "height": 800})
    
    async def _close_browser(self) -> None:
        """Close the browser instance."""
        if self.browser:
            logger.debug("Closing browser instance")
            await self.browser.close()
            self.browser = None
            self.page = None
    
    async def _search_web(self, query: str) -> List[Dict[str, str]]:
        """
        Search the web for the given query.
        
        Args:
            query: Search query string
            
        Returns:
            List of search results with title, url, and snippet
        """
        logger.info(f"Searching web for: {query}")
        
        # Set up the browser if needed
        if not self.browser or not self.page:
            await self._setup_browser()
        
        # Navigate to a search engine
        logger.debug("Navigating to search engine")
        await self.page.goto("https://www.google.com/", timeout=self.timeout)
        
        # Type in the search query
        logger.debug("Entering search query")
        await self.page.fill('input[name="q"]', query)
        await self.page.press('input[name="q"]', "Enter")
        
        # Wait for results to load
        logger.debug("Waiting for search results")
        await self.page.wait_for_selector('div#search', timeout=self.timeout)
        
        # Extract search results
        logger.debug("Extracting search results")
        results = []
        
        # Wait a bit for JavaScript to render results
        await asyncio.sleep(1)
        
        # Get search result elements
        result_elements = await self.page.query_selector_all('div.g')
        
        for i, result in enumerate(result_elements):
            if i >= self.max_results:
                break
                
            try:
                # Extract title
                title_element = await result.query_selector('h3')
                title = await title_element.inner_text() if title_element else "No title"
                
                # Extract URL
                link_element = await result.query_selector('a')
                url = await link_element.get_attribute('href') if link_element else ""
                
                # Extract snippet
                snippet_element = await result.query_selector('div.VwiC3b')
                snippet = await snippet_element.inner_text() if snippet_element else "No snippet available"
                
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet
                })
                
                logger.debug(f"Found result: {title}")
            except Exception as e:
                logger.error(f"Error extracting search result: {str(e)}")
        
        return results
    
    def execute(self, query: str) -> Dict[str, Any]:
        """
        Execute a web search.
        
        Args:
            query: The search query
            
        Returns:
            Dictionary with search results or error
        """
        if not PLAYWRIGHT_AVAILABLE:
            return {
                "status": "error",
                "error": "Playwright not available. Please install with: pip install playwright"
            }
        
        try:
            # Run the async search function
            logger.info(f"Executing web search for: {query}")
            results = asyncio.run(self._run_search(query))
            
            # Format the results
            formatted_results = self._format_results(results)
            
            return {
                "status": "success",
                "result": formatted_results,
                "query": query,
                "count": len(results)
            }
        except Exception as e:
            logger.error(f"Error executing web search: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "query": query
            }
    
    async def _run_search(self, query: str) -> List[Dict[str, str]]:
        """Run the search and cleanup."""
        try:
            results = await self._search_web(query)
            return results
        finally:
            await self._close_browser()
    
    def _format_results(self, results: List[Dict[str, str]]) -> str:
        """
        Format search results into a readable string.
        
        Args:
            results: List of search result dictionaries
            
        Returns:
            Formatted results string
        """
        if not results:
            return "No results found."
        
        formatted = f"Found {len(results)} results:\n\n"
        
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result['title']}\n"
            formatted += f"   URL: {result['url']}\n"
            formatted += f"   {result['snippet']}\n\n"
        
        return formatted
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the web browser tool.
        
        Returns:
            Dictionary with tool information
        """
        return {
            "name": self.name,
            "description": self.description,
            "usage": "web_browser.execute('search query')",
            "examples": [
                "web_browser.execute('latest news about AI')",
                "web_browser.execute('python programming tutorials')",
                "web_browser.execute('weather in New York')"
            ],
            "requires": "playwright"
        } 