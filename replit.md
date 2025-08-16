# Overview

This is a Python Flask web application that scrapes and extracts comprehensive business insights from Shopify stores without using official APIs. The application provides a web interface and REST API endpoint that accepts a Shopify store URL and returns structured JSON data containing product catalogs, policies, contact information, social media handles, and other business intelligence.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Web Interface**: Single-page application using Bootstrap 5 with dark theme
- **Responsive Design**: Mobile-first approach with Bootstrap grid system
- **Client-Side Interactions**: Vanilla JavaScript for form handling and API communication
- **UI Components**: Card-based layout with accordions for organizing scraped data
- **Styling**: Custom CSS combined with Bootstrap components and Font Awesome icons

## Backend Architecture
- **Web Framework**: Flask application with RESTful API design
- **Application Structure**: Modular design separating web scraping logic from API routes
- **Error Handling**: Comprehensive exception handling with proper HTTP status codes
- **Logging**: Built-in Python logging for debugging and monitoring
- **Session Management**: Flask sessions with configurable secret key

## Data Extraction Engine
- **Web Scraping**: Custom `ShopifyScraper` class using requests and BeautifulSoup
- **Content Parsing**: Trafilatura library for advanced text extraction
- **Data Sources**: Multiple extraction methods including JSON endpoints and HTML parsing
- **URL Normalization**: Automatic URL formatting and validation
- **Request Handling**: Session-based requests with proper headers and timeout management

## API Design
- **RESTful Endpoints**: Clean API structure with dedicated routes for health checks and data fetching
- **Input Validation**: JSON request validation with proper error responses
- **Response Format**: Structured JSON output with consistent error handling
- **Content Types**: Support for JSON request/response with proper MIME types

## Security Considerations
- **User Agent Spoofing**: Browser-like headers to avoid bot detection
- **Rate Limiting**: Session-based requests to prevent aggressive scraping
- **Input Sanitization**: URL validation and normalization
- **Error Masking**: Generic error messages to prevent information leakage

# External Dependencies

## Python Libraries
- **Flask**: Web framework for API and routing
- **requests**: HTTP client for web scraping
- **BeautifulSoup4**: HTML parsing and DOM manipulation
- **trafilatura**: Advanced web content extraction
- **urllib.parse**: URL parsing and manipulation utilities

## Frontend Dependencies
- **Bootstrap 5**: CSS framework with dark theme variant
- **Font Awesome**: Icon library for UI elements
- **CDN Delivery**: External resources loaded via CDN for performance

## Target Platform Integration
- **Shopify Stores**: Specialized scraping logic for Shopify's common patterns
- **JSON Endpoints**: Direct access to `/products.json` for product data
- **HTML Parsing**: Fallback parsing for pages without JSON endpoints
- **Social Media Platforms**: Extraction of social media handles and links

## Development Dependencies
- **Python 3.x**: Runtime environment
- **Environment Variables**: Configuration through environment variables
- **Debug Mode**: Development server with hot reloading capabilities