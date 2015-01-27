#!/usr/bin/env python
#-*- coding: utf-8 -*-

##     PySitemap - A simple Python module to create XML sitemaps with
##                 support for sitemap indexes for very large maps.
##
##     For more information about sitemap indexes see:
##        http://www.sitemaps.org/protocol.html#index
##        http://www.mugo.ca/Blog/Google-Sitemaps-for-big-sites-splitting-the-sitemap-into-multiple-files
##
##     Copyright (C) 2015  Roy Firestein <roy @@@ firestein ... net>
##     Based on ApeSmit <https://pypi.python.org/pypi/apesmit/0.01>

##     This program is free software; you can redistribute it and/or modify
##     it under the terms of the GNU General Public License as published by
##     the Free Software Foundation; either version 2 of the License, or
##     (at your option) any later version.

##     This program is distributed in the hope that it will be useful,
##     but WITHOUT ANY WARRANTY; without even the implied warranty of
##     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##     GNU General Public License for more details.

##     You should have received a copy of the GNU General Public License along
##     with this program; if not, write to the Free Software Foundation, Inc.,
##     51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


import datetime, codecs

FREQ=set((None, 'always', 'hourly', 'daily', 'weekly', 'monthly',
          'yearly', 'never'))  #: values for changefreq

     
class Url(object):
    """
    Class to handle a URL in `Sitemap`
    """
    def __init__(self, loc, lastmod, changefreq, priority, escape=True):
        """
        Constructor

        :Parameters:
          loc : string
            Location (URL). See http://www.sitemaps.org/protocol.php#locdef
          lastmod : ``datetime.date`` or ``string``
            Date of last modification.
            See http://www.sitemaps.org/protocol.php#lastmoddef
            The ``today`` is replaced by today's date
          changefreq : One of the values in `FREQ`
            Expected frequency for changes.
            See http://www.sitemaps.org/protocol.php#changefreqdef
          priority : ``float`` or ``string``
            Priority of this URL relative to other URLs on your site.
            See http://www.sitemaps.org/protocol.php#prioritydef
          escape
            True if escaping for XML special characters should be done.
            See http://www.sitemaps.org/protocol.php#escaping        
        """
        if escape:            
            self.loc=self.escape(loc)
        else:
            self.loc=loc
        if lastmod=='today':
            lastmod=datetime.date.today().isoformat()
        if lastmod is not None:
            self.lastmod=unicode(lastmod)
        else:
            self.lastmod=None
        if changefreq not in FREQ:
            raise ValueError("Invalid changefreq value: '%s'"%changefreq)
        if changefreq is not None:
            self.changefreq=unicode(changefreq)
        else:
            self.changefreq=None
        if priority is not None:
            self.priority=unicode(priority)
        else:
            self.priority=None
        self.urls=[]

    def escape(self, s):
        """
        Escaping XML special chracters

        :Parameters:
          s
            String to escape
        :return: Escaped string
        """
        s=s.replace('&', '&amp;')
        s=s.replace("'", '&apos;')
        s=s.replace('"', '&quod;')
        s=s.replace('>', '&gt;')
        s=s.replace('<', '&lt;')
        return s
    
class Sitemap(object):
    """
    Class to manage a sitemap
    """
    def __init__(self, lastmod=None, changefreq=None, priority=None, sitemap_url='/'):
        """
        Constructor

        :Parameters:
          lastmod
             Default value for `lastmod`. See `Url.__init__()`.
          changefreq
             Default value for `changefreq`. See `Url.__init__()`.
          priority
             Default value for `priority`. See `Url.__init__()`.
        """
        
        self.lastmod=lastmod
        self.changefreq=changefreq
        self.priority=priority
        self.urls=[]
        
        self.sitemaps = []
        self.index_required = False
        self.sitemap_url = sitemap_url


    def add(self, loc, lastmod=None, changefreq=None, priority=None, escape=True):
        """
        Add a new URl. Parameters are the same as in  `Url.__init__()`.
        If ``lastmod``, ``changefreq`` or ``priority`` is ``None`` the default
        value is used (see `__init__()`)
        """
        
        if lastmod is None:
            lastmod=self.lastmod
        if changefreq is None:
            changefreq=self.changefreq
        if priority is None:
            priority=self.priority
        self.urls.append(Url(loc, lastmod, changefreq, priority, escape))

            
    def write(self, file_name='sitemap'):
        """
        Write sitemap to ``out``

        :Parameters:
           out
             file name or anything with a ``write()`` method  
        """
        
        if '.xml' in file_name:
            file_name = file_name.replace('.xml','')
        
        if len(self.urls) > 50000:
            self.index_required = True         
        
        count = 1
        for chunk in self._chunks(self.urls):
            output_file_name = "%s.xml" %(file_name)
            if self.index_required:
                output_file_name = "%s%s.xml" %(file_name, count)
            
            try:
                fh = codecs.open(output_file_name, 'w', 'utf-8')
            except Exception, e:
                print "Can't open file '%s': %s"%(output_file_name, str(e))
                return
            
            fh.write("<?xml version='1.0' encoding='UTF-8'?>\n"
                    '<urlset xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
                    '        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9\n'
                    '        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd"\n'
                    '        xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
            
            for url in chunk:
                lastmod=changefreq=priority=''
                if url.lastmod is not None:
                    lastmod='  <lastmod>%s</lastmod>\n'%url.lastmod
                if url.changefreq is not None:
                    changefreq='  <changefreq>%s</changefreq>\n'%url.changefreq
                if url.priority is not None:
                    priority='  <priority>%s</priority>\n'%url.priority
                fh.write(" <url>\n"
                         "  <loc>%s</loc>\n%s%s%s"
                         " </url>\n"%(url.loc.decode('utf-8'),
                                      lastmod.decode('utf-8'),
                                      changefreq.decode('utf-8'),
                                      priority.decode('utf-8')))
            fh.write('</urlset>\n')
            fh.close()
            self.sitemaps.append(output_file_name)
            count += 1
        
        if self.index_required:
            self._write_sitemaps_index(file_name)
        print "Sitemap created."
            
    
    def _write_sitemaps_index(self, file_name):
        try:
            fh = codecs.open("%s.xml" %(file_name), 'w', 'utf-8')
        except Exception, e:
            print "Can't open file '%s.xml': %s"%(file_name, str(e))
            return
        
        fh.write("<?xml version='1.0' encoding='UTF-8'?>\n"
                '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        
        for sitemap in self.sitemaps:
            fh.write("<sitemap>\n"
                     "<loc>%s%s</loc>\n"
                     "<lastmod>%s</lastmod>\n"
                     "<sitemap>\n" %(
                         self.sitemap_url.decode('utf-8'),
                         sitemap.decode('utf-8'),
                         datetime.datetime.utcnow().strftime("%Y-%m-%d")
                     )
             )
        
        fh.write('</sitemapindex>\n')
    
    
    def _chunks(self, l, n=50000):
        return [l[i:i+n] for i in range(0, len(l), n)]

