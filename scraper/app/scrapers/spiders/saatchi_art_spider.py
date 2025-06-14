"""
SaatchiArt Spider
For scraping artist and artwork information from SaatchiArt website
"""
import json
import logging
import time
from typing import Dict, List, Any, Optional, Union

from playwright.sync_api import Page
from scrapy import Selector

from app.scrapers.playwright_spider import PlaywrightSpider

logger = logging.getLogger(__name__)


class SaatchiArtSpider(PlaywrightSpider):
    """
    SaatchiArt spider class
    Scrapes artist and artwork information
    """
    name = "saatchi_art"
    
    def setup_playwright(self, page: Page) -> None:
        """
        Set up Playwright
        
        Args:
            page: Playwright page object
        """
        super().setup_playwright(page)
        # Set page viewport size
        page.set_viewport_size({"width": 1280, "height": 800})
        
        # Set interceptors to ignore images and fonts, speeding up loading
        page.route("**/*.{png,jpg,jpeg,gif,webp,svg}", lambda route: route.abort())
        page.route("**/*.{woff,woff2,ttf,otf,eot}", lambda route: route.abort())
        
        logger.info("Playwright setup completed for SaatchiArt")
    
    def start_scraping(self) -> None:
        """
        Start scraping
        """
        # Get configuration
        max_pages = self.config.get("max_pages", 3)
        max_artists = self.config.get("max_items_per_category", 50)
        
        # Scrape artists
        self.scrape_artists(max_pages, max_artists)
        
        # Scrape artworks
        self.scrape_artworks(max_pages, max_artists)
    
    def scrape_artists(self, max_pages: int, max_artists: int) -> None:
        """
        Scrape artist information
        
        Args:
            max_pages: Maximum number of pages
            max_artists: Maximum number of artists
        """
        logger.info("Starting to scrape SaatchiArt artist information")
        
        # Artist list page
        artists_url = "https://www.saatchiart.com/artists"
        self.page.goto(artists_url)
        self.wait_for_page_load()
        
        artists_scraped = 0
        pages_scraped = 0
        
        while pages_scraped < max_pages and artists_scraped < max_artists:
            # Wait for artist cards to load
            self.page.wait_for_selector(".artists-grid .artist-card", timeout=10000)
            
            # Get current page content
            content = self.page.content()
            selector = Selector(text=content)
            
            # Extract artist cards
            artist_cards = selector.css(".artists-grid .artist-card")
            logger.info(f"Found {len(artist_cards)} artist cards")
            
            # Process each artist
            for artist_card in artist_cards:
                if artists_scraped >= max_artists:
                    break
                
                try:
                    # Extract artist information
                    artist_data = self.extract_artist_data(artist_card)
                    if artist_data:
                        # Save artist data
                        self.save_item(artist_data)
                        artists_scraped += 1
                        logger.info(f"Scraped {artists_scraped}/{max_artists} artists")
                except Exception as e:
                    logger.error(f"Error processing artist: {str(e)}")
            
            # Check if there is a next page
            next_button = self.page.query_selector("a.next-page:not(.disabled)")
            if next_button:
                # Click next page
                next_button.click()
                self.wait_for_page_load()
                pages_scraped += 1
                logger.info(f"Scraped {pages_scraped}/{max_pages} artist pages")
            else:
                logger.info("No more artist pages")
                break
        
        logger.info(f"Artist scraping completed, scraped {artists_scraped} artists")
    
    def extract_artist_data(self, artist_card: Selector) -> Dict[str, Any]:
        """
        Extract data from artist card
        
        Args:
            artist_card: Artist card selector
            
        Returns:
            Dict[str, Any]: Artist data
        """
        try:
            # Extract basic information
            name = artist_card.css(".artist-name::text").get("").strip()
            location = artist_card.css(".artist-location::text").get("").strip()
            url = artist_card.css("a.artist-link::attr(href)").get("")
            
            # Build complete URL
            if url and not url.startswith("http"):
                url = f"https://www.saatchiart.com{url}"
            
            # Extract artist image
            image_url = artist_card.css(".artist-image img::attr(src)").get("")
            
            # Build artist data
            artist_data = {
                "page_type": "artist",
                "name": name,
                "location": location,
                "url": url,
                "image_url": image_url,
                "source": "saatchiart",
                "data": {
                    "followers": artist_card.css(".artist-stats .followers-count::text").get("0").strip(),
                    "artworks": artist_card.css(".artist-stats .artworks-count::text").get("0").strip()
                }
            }
            
            return artist_data
        except Exception as e:
            logger.error(f"Error extracting artist data: {str(e)}")
            return {}
    
    def scrape_artworks(self, max_pages: int, max_artworks: int) -> None:
        """
        Scrape artwork information
        
        Args:
            max_pages: Maximum number of pages
            max_artworks: Maximum number of artworks
        """
        logger.info("Starting to scrape SaatchiArt artwork information")
        
        # Artwork list page
        artworks_url = "https://www.saatchiart.com/paintings"
        self.page.goto(artworks_url)
        self.wait_for_page_load()
        
        artworks_scraped = 0
        pages_scraped = 0
        
        while pages_scraped < max_pages and artworks_scraped < max_artworks:
            # Wait for artwork cards to load
            self.page.wait_for_selector(".artworks-grid .artwork-item", timeout=10000)
            
            # Get current page content
            content = self.page.content()
            selector = Selector(text=content)
            
            # Extract artwork cards
            artwork_cards = selector.css(".artworks-grid .artwork-item")
            logger.info(f"Found {len(artwork_cards)} artwork cards")
            
            # Process each artwork
            for artwork_card in artwork_cards:
                if artworks_scraped >= max_artworks:
                    break
                
                try:
                    # Extract artwork information
                    artwork_data = self.extract_artwork_data(artwork_card)
                    if artwork_data:
                        # Save artwork data
                        self.save_item(artwork_data)
                        artworks_scraped += 1
                        logger.info(f"Scraped {artworks_scraped}/{max_artworks} artworks")
                except Exception as e:
                    logger.error(f"Error processing artwork: {str(e)}")
            
            # Check if there is a next page
            next_button = self.page.query_selector("a.next-page:not(.disabled)")
            if next_button:
                # Click next page
                next_button.click()
                self.wait_for_page_load()
                pages_scraped += 1
                logger.info(f"Scraped {pages_scraped}/{max_pages} artwork pages")
            else:
                logger.info("No more artwork pages")
                break
        
        logger.info(f"Artwork scraping completed, scraped {artworks_scraped} artworks")
    
    def extract_artwork_data(self, artwork_card: Selector) -> Dict[str, Any]:
        """
        Extract data from artwork card
        
        Args:
            artwork_card: Artwork card selector
            
        Returns:
            Dict[str, Any]: Artwork data
        """
        try:
            # Extract basic information
            title = artwork_card.css(".artwork-title::text").get("").strip()
            artist_name = artwork_card.css(".artwork-artist::text").get("").strip()
            url = artwork_card.css("a.artwork-link::attr(href)").get("")
            
            # Build complete URL
            if url and not url.startswith("http"):
                url = f"https://www.saatchiart.com{url}"
            
            # Extract artwork image
            image_url = artwork_card.css(".artwork-image img::attr(src)").get("")
            
            # Extract price
            price = artwork_card.css(".artwork-price::text").get("").strip()
            
            # Extract dimensions and medium
            details = artwork_card.css(".artwork-details::text").get("").strip()
            
            # Build artwork data
            artwork_data = {
                "page_type": "artwork",
                "title": title,
                "artist_name": artist_name,
                "url": url,
                "image_url": image_url,
                "source": "saatchiart",
                "data": {
                    "price": price,
                    "details": details,
                    "likes": artwork_card.css(".artwork-likes-count::text").get("0").strip()
                }
            }
            
            return artwork_data
        except Exception as e:
            logger.error(f"Error extracting artwork data: {str(e)}")
            return {}
    
    def wait_for_page_load(self) -> None:
        """
        Wait for page to load completely
        """
        # Wait for page to load
        self.page.wait_for_load_state("networkidle", timeout=30000)
        
        # Wait extra time to ensure JavaScript rendering is complete
        time.sleep(2)
        
        # Scroll page to load more content
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        time.sleep(1)
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1) 