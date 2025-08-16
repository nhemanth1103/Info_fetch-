import requests
import re
import logging
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import trafilatura
import json

class ShopifyScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.timeout = 10
        
    def normalize_url(self, url):
        """Normalize URL to ensure proper format"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url.rstrip('/')
    
    def fetch_page(self, url):
        """Fetch a web page with error handling"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch {url}: {str(e)}")
            return None
    
    def extract_products_json(self, base_url):
        """Extract products from /products.json endpoint"""
        products_url = urljoin(base_url, '/products.json')
        response = self.fetch_page(products_url)
        
        if not response:
            return []
        
        try:
            data = response.json()
            products = []
            
            for product in data.get('products', []):
                product_info = {
                    'id': product.get('id'),
                    'title': product.get('title'),
                    'handle': product.get('handle'),
                    'vendor': product.get('vendor'),
                    'product_type': product.get('product_type'),
                    'tags': product.get('tags', '').split(',') if product.get('tags') else [],
                    'price_range': self.extract_price_range(product.get('variants', [])),
                    'images': [img.get('src') for img in product.get('images', [])],
                    'description': product.get('body_html', ''),
                    'available': any(variant.get('available', False) for variant in product.get('variants', []))
                }
                products.append(product_info)
            
            return products
        except (json.JSONDecodeError, KeyError) as e:
            logging.error(f"Failed to parse products JSON: {str(e)}")
            return []
    
    def extract_price_range(self, variants):
        """Extract price range from product variants"""
        if not variants:
            return None
        
        prices = [float(variant.get('price', 0)) for variant in variants if variant.get('price')]
        if not prices:
            return None
        
        min_price = min(prices)
        max_price = max(prices)
        
        if min_price == max_price:
            return {'price': min_price}
        else:
            return {'min_price': min_price, 'max_price': max_price}
    
    def extract_hero_products(self, base_url):
        """Extract featured/hero products from homepage"""
        response = self.fetch_page(base_url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        hero_products = []
        
        # Common selectors for featured products
        selectors = [
            '.featured-products .product-item',
            '.hero-products .product',
            '.collection-grid .product-card',
            '[data-product-id]',
            '.product-recommendation'
        ]
        
        for selector in selectors:
            products = soup.select(selector)
            for product in products[:6]:  # Limit to 6 featured products
                title_elem = product.select_one('.product-title, .product-name, h3, h4')
                price_elem = product.select_one('.price, .product-price')
                image_elem = product.select_one('img')
                link_elem = product.select_one('a')
                
                if title_elem:
                    hero_product = {
                        'title': title_elem.get_text(strip=True),
                        'price': price_elem.get_text(strip=True) if price_elem else None,
                        'image': image_elem.get('src') if image_elem else None,
                        'link': urljoin(base_url, link_elem.get('href')) if link_elem else None
                    }
                    hero_products.append(hero_product)
            
            if hero_products:
                break
        
        return hero_products
    
    def extract_social_handles(self, soup, base_url):
        """Extract social media handles from the page"""
        social_handles = {}
        
        # Find social media links
        social_links = soup.find_all('a', href=re.compile(r'(instagram|facebook|twitter|tiktok|youtube|linkedin|pinterest)\.com'))
        
        for link in social_links:
            href = link.get('href', '')
            if 'instagram.com' in href:
                social_handles['instagram'] = href
            elif 'facebook.com' in href:
                social_handles['facebook'] = href
            elif 'twitter.com' in href or 'x.com' in href:
                social_handles['twitter'] = href
            elif 'tiktok.com' in href:
                social_handles['tiktok'] = href
            elif 'youtube.com' in href:
                social_handles['youtube'] = href
            elif 'linkedin.com' in href:
                social_handles['linkedin'] = href
            elif 'pinterest.com' in href:
                social_handles['pinterest'] = href
        
        return social_handles
    
    def extract_contact_details(self, soup, base_url):
        """Extract contact information from the page"""
        contact_details = {}
        
        # Extract email addresses
        emails = set()
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        page_text = soup.get_text()
        found_emails = re.findall(email_pattern, page_text)
        for email in found_emails:
            if not email.endswith(('.png', '.jpg', '.gif')):  # Filter out image files
                emails.add(email)
        
        if emails:
            contact_details['emails'] = list(emails)
        
        # Extract phone numbers
        phone_pattern = r'(\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})'
        phones = set(re.findall(phone_pattern, page_text))
        if phones:
            contact_details['phones'] = list(phones)
        
        # Look for contact page link
        contact_link = soup.find('a', href=re.compile(r'contact', re.I))
        if contact_link:
            contact_details['contact_page'] = urljoin(base_url, contact_link.get('href'))
        
        return contact_details
    
    def extract_important_links(self, soup, base_url):
        """Extract important navigation and footer links"""
        important_links = {}
        
        # Common important link patterns
        link_patterns = {
            'contact': re.compile(r'contact', re.I),
            'about': re.compile(r'about', re.I),
            'shipping': re.compile(r'shipping', re.I),
            'returns': re.compile(r'return|refund', re.I),
            'privacy': re.compile(r'privacy', re.I),
            'terms': re.compile(r'terms|conditions', re.I),
            'faq': re.compile(r'faq|help', re.I),
            'blog': re.compile(r'blog|news', re.I),
            'track': re.compile(r'track|order', re.I)
        }
        
        for link_type, pattern in link_patterns.items():
            link = soup.find('a', href=pattern)
            if link:
                important_links[link_type] = urljoin(base_url, link.get('href'))
        
        return important_links
    
    def extract_page_content(self, url):
        """Extract clean text content from a page using trafilatura"""
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                text = trafilatura.extract(downloaded)
                return text[:2000] if text else None  # Limit content length
        except Exception as e:
            logging.error(f"Failed to extract content from {url}: {str(e)}")
        return None
    
    def scrape_store(self, website_url):
        """Main method to scrape all insights from a Shopify store"""
        try:
            base_url = self.normalize_url(website_url)
            
            # Test if website exists
            response = self.fetch_page(base_url)
            if not response:
                return {'error': 'Website not found or not accessible'}, 401
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract store name
            store_name = None
            title_tag = soup.find('title')
            if title_tag:
                store_name = title_tag.get_text(strip=True)
            
            # Extract all insights
            insights = {
                'store_name': store_name,
                'website_url': base_url,
                'products': self.extract_products_json(base_url),
                'hero_products': self.extract_hero_products(base_url),
                'social_handles': self.extract_social_handles(soup, base_url),
                'contact_details': self.extract_contact_details(soup, base_url),
                'important_links': self.extract_important_links(soup, base_url)
            }
            
            # Extract content from important pages
            important_links = insights['important_links']
            
            if 'privacy' in important_links:
                insights['privacy_policy'] = self.extract_page_content(important_links['privacy'])
            
            if 'returns' in important_links:
                insights['return_policy'] = self.extract_page_content(important_links['returns'])
            
            if 'about' in important_links:
                insights['brand_context'] = self.extract_page_content(important_links['about'])
            
            if 'faq' in important_links:
                insights['faqs'] = self.extract_page_content(important_links['faq'])
            
            # Add metadata
            insights['total_products'] = len(insights['products'])
            insights['scraping_timestamp'] = requests.utils.default_headers()['User-Agent']
            
            return insights
            
        except Exception as e:
            logging.error(f"Error scraping store {website_url}: {str(e)}")
            raise Exception(f"Failed to scrape store: {str(e)}")
