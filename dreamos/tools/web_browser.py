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
    
    async def _visit_website(self, url: str) -> Dict[str, Any]:
        """
        Visit a specific website URL.
        
        Args:
            url: The URL to visit
            
        Returns:
            Dictionary with visit result info
        """
        logger.info(f"Visiting website: {url}")
        
        # Make sure URL has protocol
        if not url.startswith('http'):
            url = 'https://' + url
        
        # Set up the browser if needed
        if not self.browser or not self.page:
            await self._setup_browser()
        
        try:
            # Navigate to the URL
            logger.debug(f"Navigating to URL: {url}")
            await self.page.goto(url, timeout=self.timeout)
            
            # Get page title
            title = await self.page.title()
            
            # Take a screenshot for verification (commented out for now)
            # screenshot_path = os.path.join(os.getcwd(), 'temp_screenshot.png')
            # await self.page.screenshot(path=screenshot_path)
            
            # Get page content summary
            content = await self.page.evaluate('document.body.innerText')
            content_summary = content[:1000] + '...' if len(content) > 1000 else content
            
            return {
                "status": "success",
                "title": title,
                "url": url,
                "content_summary": content_summary
            }
        except Exception as e:
            logger.error(f"Error visiting website: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "url": url
            }

    def execute(self, query: str, action: str = "search") -> Dict[str, Any]:
        """
        Execute a web browser action.
        
        Args:
            query: The search query or URL
            action: The action to perform ("search" or "visit")
            
        Returns:
            Dictionary with action results or error
        """
        if not PLAYWRIGHT_AVAILABLE:
            return {
                "status": "error",
                "error": "Playwright not available. Please install with: pip install playwright"
            }
        
        try:
            # For explicit "visit" actions or if query looks like a URL
            if action == "visit" or (
                query.startswith(('http://', 'https://')) or 
                any(query.startswith(d + '.') for d in ['www', 'youtube', 'github', 'google']) or
                any(domain in query for domain in ['.com', '.org', '.net', '.io', '.gov'])
            ):
                # Visit the website
                logger.info(f"Visiting website: {query}")
                result = asyncio.run(self._run_visit(query))
                return {
                    "status": "success",
                    "result": self._format_visit_results(result)
                }
            else:
                # Search the web
                logger.info(f"Searching for: {query}")
                results = asyncio.run(self._run_search(query))
                return {
                    "status": "success",
                    "result": self._format_results(results)
                }
        except Exception as e:
            logger.error(f"Error executing web browser tool: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": f"Web browser error: {str(e)}"
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
    
    async def _run_visit(self, url: str) -> Dict[str, Any]:
        """Run the website visit and cleanup."""
        try:
            result = await self._visit_website(url)
            return result
        finally:
            await self._close_browser()
    
    def _format_visit_results(self, result: Dict[str, Any]) -> str:
        """
        Format website visit results into a readable string.
        
        Args:
            result: Visit result dictionary
            
        Returns:
            Formatted visit result string
        """
        if result.get("status") != "success":
            return f"Failed to visit website: {result.get('error', 'Unknown error')}"
        
        formatted = f"Successfully visited: {result.get('title', 'Unknown title')}\n"
        formatted += f"URL: {result.get('url')}\n\n"
        formatted += "Page content summary:\n"
        formatted += result.get('content_summary', 'No content available')
        
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