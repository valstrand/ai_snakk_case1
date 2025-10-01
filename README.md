# AI-Snakk Website

A modern, mobile-first website for AI-Snakk - a community for practical AI talks, demos, and case studies for Nordic business and tech.

## Features

- **Modern Design**: Clean, AI-inspired aesthetic with glassmorphism effects and gradients
- **Mobile-First**: Fully responsive design optimized for all devices
- **Dark/Light Mode**: Toggle between themes with persistent user preference
- **Content Management**: Full Django Admin interface for managing content
- **SEO Optimized**: Meta tags, Open Graph, Twitter cards, sitemaps, and RSS feeds
- **Performance**: Optimized images, lazy loading, and Core Web Vitals friendly
- **Accessibility**: Semantic HTML, ARIA labels, keyboard navigation support

## Tech Stack

- **Backend**: Django 5.0.7 with PostgreSQL/SQLite
- **Frontend**: Tailwind CSS with custom AI-inspired styling
- **Rich Text**: CKEditor for content editing
- **Deployment**: Docker with Nginx reverse proxy
- **Security**: CSRF protection, security headers, input validation

## Quick Start

### Local Development

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd ai-snakk-website
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup database**:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Run development server**:
   ```bash
   python manage.py runserver
   ```

5. **Access the site**:
   - Website: http://localhost:8000
   - Admin: http://localhost:8000/admin

### Docker Deployment

1. **Build and run with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

2. **Setup database (first time only)**:
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

3. **Access the site**:
   - Website: http://localhost
   - Admin: http://localhost/admin

## Site Structure

### Public Pages

- **Home (/)**: Hero section, featured event, latest posts, presentations/cases highlights
- **Blog (/blog)**: Blog listing with search/filtering, individual post pages, RSS feed
- **Events (/events)**: Upcoming and past events, event detail pages
- **About (/about)**: Community information and mission
- **Contact (/contact)**: Contact form with spam protection

### Admin Content Management

Access the admin at `/admin` to manage:

- **Blog Posts**: Title, content, cover images, tags, SEO fields, publishing
- **Events**: Event details, RSVP links, featured event selection
- **Case Studies**: Client work and success stories
- **Presentations**: Talk recordings and slides
- **Site Settings**: Logo, social links, contact info, analytics

## Content Models

### Blog Posts
- Title, slug, author, summary, rich text body
- Cover image, tags, reading time estimation
- SEO fields (title, description)
- Publishing workflow (draft → scheduled → published)

### Events
- Title, slug, start/end dates (Europe/Oslo timezone)
- Location and/or streaming URL
- Descriptions, hero image, capacity, RSVP link
- Featured event flag (only one active)

### Case Studies
- Client, industry, summary, detailed body
- Metrics (ROI, cost savings, time savings)
- Cover image, tags, publishing workflow

### Presentations
- Speaker info, slides/video links
- Event association, presentation date
- Cover image, tags, publishing workflow

## Environment Variables

Key environment variables (see `.env.example`):

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com

# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# Email
EMAIL_HOST=smtp.example.com
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-password

# Analytics
ANALYTICS_ID=GA_MEASUREMENT_ID
```

## Customization

### Styling
- Main colors defined in Tailwind config: `ai-blue`, `ai-purple`, `ai-green`
- Custom CSS in `templates/base.html` for glassmorphism effects
- Dark/light mode toggle with localStorage persistence

### Content
- Site settings managed through Django admin
- Logo upload with fallback to default AI icon
- Social media links and contact information
- Brand name and description customizable

## SEO Features

- Automatic sitemap generation (`/sitemap.xml`)
- RSS feed for blog posts (`/blog/rss.xml`)
- Open Graph and Twitter card meta tags
- JSON-LD structured data for articles and events
- Canonical URLs and proper meta descriptions

## Security

- CSRF protection on all forms
- Honeypot spam protection on contact form
- Security middleware with proper headers
- Input validation and sanitization
- Rate limiting ready (configure in production)

## Performance

- Responsive images with lazy loading
- Static file compression via Nginx
- Optimized queries with select_related/prefetch_related
- Tailwind CSS via CDN for development
- WhiteNoise for static file serving

## Production Deployment

1. **Environment Setup**:
   - Set `DEBUG=False`
   - Configure production database
   - Set up email backend
   - Add analytics tracking

2. **Security Checklist**:
   - Generate strong `SECRET_KEY`
   - Enable HTTPS and security headers
   - Configure ALLOWED_HOSTS
   - Review CSP settings in nginx.conf

3. **Performance**:
   - Enable database connection pooling
   - Configure Redis for caching (optional)
   - Set up CDN for static files (optional)
   - Monitor with logging/APM tools

## Content Management Guide

### Creating Blog Posts
1. Go to Admin → Blog Posts → Add
2. Fill in title (slug auto-generates)
3. Write summary and rich text body
4. Upload cover image (optional)
5. Add tags for categorization
6. Set publishing date and status
7. Configure SEO fields

### Managing Events
1. Go to Admin → Events → Add
2. Set title, dates, and timezone
3. Add location or streaming URL
4. Write descriptions (short for listings, full for detail)
5. Upload hero image
6. Mark as featured for homepage display
7. Add RSVP link if external ticketing

### Site Configuration
1. Go to Admin → Site Settings
2. Upload logo and set brand name
3. Configure social media links
4. Set contact email and description
5. Add analytics tracking ID

## Development

### Adding New Features
1. Create Django app: `python manage.py startapp appname`
2. Add to `INSTALLED_APPS` in settings
3. Create models, views, templates
4. Update URL routing
5. Add admin configuration
6. Run migrations: `python manage.py makemigrations && python manage.py migrate`

### Running Tests
```bash
python manage.py test
```

### Code Quality
```bash
# Django check
python manage.py check

# Security check
python manage.py check --deploy
```

## Support

For issues and feature requests:
1. Check existing documentation
2. Review Django logs for errors
3. Verify environment configuration
4. Check database connectivity

## License

This project is designed for AI-Snakk community use. Modify and distribute as needed for your organization.

---

**AI-Snakk** - Practical AI for Nordic business and tech.