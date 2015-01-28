# python-sitemap-generator
A simple Python module to create XML sitemaps with support for sitemap index files.

`pysitemapgen` will create appropriate sitemap index files (to group multiple sitemap files) for maps with more than 50,000 URLs.

For more details about Sitemap index files, see:
+ http://www.sitemaps.org/protocol.html#index

Example usage:

```
from pysitemapgen import Sitemap

sm=Sitemap(changefreq='weekly', sitemap_url='http://example.com/')

for x in range(1,150000):
  sm.add('http://www.example.com/page-%s.html' %x,
        changefreq='daily',
        priority=0.7,
        lastmod='2015-27-01')

sm.write('sitemap')
```

You should get 4 files for the example above:

```
sitemap.xml  sitemap1.xml  sitemap2.xml  sitemap3.xml
```

Contents of `sitemap.xml`:

```
<?xml version='1.0' encoding='UTF-8'?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <sitemap>
        <loc>http://example.com/sitemap1.xml</loc>
        <lastmod>2015-01-26</lastmod>
    </sitemap>
    <sitemap>
        <loc>http://example.com/sitemap2.xml</loc>
        <lastmod>2015-01-26</lastmod>
    </sitemap>
    <sitemap>
        <loc>http://example.com/sitemap3.xml</loc>
        <lastmod>2015-01-26</lastmod>
    </sitemap>
</sitemapindex>
```
