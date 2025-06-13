#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Website and Scraper Management CLI Tool
"""
import os
import sys
import argparse
import logging
from typing import Dict, List, Any, Optional

from .site_manager import WebsiteManager
from .registry import ScraperRegistry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class WebsiteManagerCLI:
    """Command line interface for managing website scrapers"""
    
    def __init__(self):
        """Initialize the CLI with a WebsiteManager"""
        registry = ScraperRegistry(config_path='config/sites_registry.json')
        self.manager = WebsiteManager(registry=registry)
        
        # Ensure config directory exists
        os.makedirs('config', exist_ok=True)
    
    def run(self, args: Optional[List[str]] = None) -> None:
        """
        Run the CLI with the given arguments
        
        Args:
            args: Command line arguments (uses sys.argv if not provided)
        """
        parser = self._create_parser()
        parsed_args = parser.parse_args(args)
        
        # Execute the appropriate command
        if not hasattr(parsed_args, 'command'):
            parser.print_help()
            return
            
        if parsed_args.command == 'list':
            self._list_websites(parsed_args)
        elif parsed_args.command == 'add':
            self._add_website(parsed_args)
        elif parsed_args.command == 'remove':
            self._remove_website(parsed_args)
        elif parsed_args.command == 'create-scraper':
            self._create_scraper(parsed_args)
        elif parsed_args.command == 'run':
            self._run_scraper(parsed_args)
        else:
            parser.print_help()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser"""
        parser = argparse.ArgumentParser(
            description='Art Website and Scraper Management Tool',
            formatter_class=argparse.RawTextHelpFormatter
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Command to execute')
        
        # List websites command
        list_parser = subparsers.add_parser('list', help='List all registered websites')
        list_parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed information')
        
        # Add website command
        add_parser = subparsers.add_parser('add', help='Add a new website')
        add_parser.add_argument('--id', required=True, help='Website ID (e.g., "met_museum")')
        add_parser.add_argument('--name', required=True, help='Website name (e.g., "Metropolitan Museum of Art")')
        add_parser.add_argument('--url', required=True, help='Website URL (e.g., "https://www.metmuseum.org")')
        add_parser.add_argument('--description', help='Website description', default='')
        
        # Remove website command
        remove_parser = subparsers.add_parser('remove', help='Remove a website')
        remove_parser.add_argument('--id', required=True, help='Website ID to remove')
        remove_parser.add_argument('--force', action='store_true', help='Force removal without confirmation')
        
        # Create scraper command
        create_parser = subparsers.add_parser('create-scraper', help='Create a new website scraper')
        create_parser.add_argument('--id', required=True, help='Website ID (e.g., "met_museum")')
        create_parser.add_argument('--name', required=True, help='Scraper name (e.g., "MetMuseum")')
        create_parser.add_argument('--url', help='Website URL if not already registered')
        
        # Run scraper command
        run_parser = subparsers.add_parser('run', help='Run a website scraper')
        run_parser.add_argument('--id', required=True, help='Website ID')
        run_parser.add_argument('--task', help='Task name (optional)')
        run_parser.add_argument('--content', choices=['artworks', 'artists', 'exhibitions'], 
                               default='artworks', help='Content type to scrape')
        run_parser.add_argument('--pages', type=int, default=1, help='Maximum pages to scrape')
        run_parser.add_argument('--limit', type=int, default=20, help='Items per page')
        
        return parser
    
    def _list_websites(self, args: argparse.Namespace) -> None:
        """List all registered websites"""
        websites = self.manager.list_websites()
        
        if not websites:
            print("No websites registered. Add one with the 'add' command.")
            return
            
        print(f"\nRegistered Websites ({len(websites)}):")
        print("-" * 80)
        
        for i, website in enumerate(websites, 1):
            print(f"{i}. {website['name']} [{website['id']}]")
            if args.verbose:
                print(f"   URL: {website['url']}")
                print(f"   Description: {website.get('description', 'No description')}")
                
                # List scrapers for this website
                scrapers = self.manager.get_website_scrapers(website['id'])
                if scrapers:
                    print(f"   Scrapers ({len(scrapers)}):")
                    for scraper in scrapers:
                        print(f"     - {scraper['task_name']} ({scraper['scraper_id']})")
                else:
                    print("   No scrapers associated")
                print()
            
        print("-" * 80)
    
    def _add_website(self, args: argparse.Namespace) -> None:
        """Add a new website"""
        try:
            website = self.manager.add_website(
                website_id=args.id,
                name=args.name,
                url=args.url,
                description=args.description
            )
            
            print(f"\nAdded website: {website['name']} [{website['id']}]")
            print(f"URL: {website['url']}")
            print(f"To create a scraper for this site, use:")
            print(f"  python -m src.scrapers.site_cli create-scraper --id {website['id']} --name {website['name'].replace(' ', '')}")
            
        except Exception as e:
            print(f"Error adding website: {str(e)}")
    
    def _remove_website(self, args: argparse.Namespace) -> None:
        """Remove a website"""
        website = self.manager.get_website(args.id)
        if not website:
            print(f"Website not found: {args.id}")
            return
            
        if not args.force:
            confirm = input(f"Are you sure you want to remove the website '{website['name']}'? (y/N): ")
            if confirm.lower() != 'y':
                print("Operation cancelled.")
                return
                
        success = self.manager.remove_website(args.id)
        if success:
            print(f"Website removed: {website['name']} [{args.id}]")
        else:
            print(f"Failed to remove website: {args.id}")
    
    def _create_scraper(self, args: argparse.Namespace) -> None:
        """Create a new website scraper"""
        try:
            # Check if website exists
            website = self.manager.get_website(args.id)
            website_name = args.name
            website_url = args.url
            
            if website:
                website_name = website['name']
                website_url = website['url']
            
            file_path = self.manager.create_site_scraper(
                website_id=args.id,
                scraper_name=args.name,
                website_name=website_name,
                website_url=website_url
            )
            
            print(f"\nCreated scraper for {website_name}")
            print(f"Scraper file: {file_path}")
            print(f"To run this scraper, use:")
            print(f"  python -m src.scrapers.site_cli run --id {args.id}")
            
        except Exception as e:
            print(f"Error creating scraper: {str(e)}")
    
    def _run_scraper(self, args: argparse.Namespace) -> None:
        """Run a website scraper"""
        try:
            # Check if website exists
            website = self.manager.get_website(args.id)
            if not website:
                print(f"Website not found: {args.id}")
                return
                
            # Run the scraper
            print(f"Running {args.content} scraper for {website['name']}...")
            print(f"Max pages: {args.pages}, Items per page: {args.limit}")
            
            result = self.manager.run_website_scraper(
                website_id=args.id,
                task_name=args.task,
                content_type=args.content,
                max_pages=args.pages,
                limit=args.limit
            )
            
            print("\nScraper finished")
            print(f"Status: {result['status']}")
            print(f"Duration: {result['duration']:.2f} seconds")
            print(f"Results: {result['results_count']} items")
            
            if 'artwork_count' in result:
                print(f"Artworks: {result['artwork_count']}")
            if 'artist_count' in result:
                print(f"Artists: {result['artist_count']}")
                
            if result['errors_count'] > 0:
                print(f"\nErrors ({result['errors_count']}):")
                for error in result['errors']:
                    print(f"  - {error}")
            
        except Exception as e:
            print(f"Error running scraper: {str(e)}")


def main():
    """Main entry point for the CLI"""
    cli = WebsiteManagerCLI()
    cli.run()


if __name__ == "__main__":
    main() 