import os, re, json, textwrap
from colorama import Fore, Style
from flashtext import KeywordProcessor

from .wordReader import WordReader

class Weekly():
    """Weekly Newsletter Class."""

    def __init__(self, config):
        self.config = config
        self.kwp = KeywordProcessor()
        self.wr = WordReader()
        self.skeleton = self.skeleton()
        self.new_html = ''

        self.docs = ['ENU.docx', 'ESN.docx', 'PTB.docx']

        self.titles = {
            "language": "",
            "calendar_title": "",
            "calendar_title_event": "",
            "calendar_title_date": "",
            "calendar_title_location": "",
            "quick_links_title": "",
            "quick_links_cta_title": ""
        }
        self.to_fill = {
            "page_title": "",
            "date": "",
            "headline": "",
            "featured": "",
            "events": "",
            "articles": "",
            "quick_links": "",
            "social": ""
        }


    def clean_text(self, text):
        text = text.strip()
        text = re.sub("[ \t]+", " ", text)
        text = re.sub(" , ", ", ", text)
        text = re.sub(" : ", ": ", text)
        return text


    def get_file(self, file):
        f = open(file, "r")
        text = f.read()
        f.close()
        return text


    def create_link(self, title, link):
        anchor = '<a href="{}" target="_blank" style="text-decoration:underline; color:#000000;">{}</a>'
        return anchor.format(link, self.clean_text(title))


    def skeleton(self):
        """Gets the skeleton for the html template."""
        return self.get_file("templates/weekly.html")


    def alert(self, msg, type='error'):
        if type == 'error':
            print(Fore.RED + msg)
        elif type == 'success':
            print(Fore.GREEN + msg)

        print(Style.RESET_ALL)


    def get_titles(self, lang):
        """Gets the standard variables for the newsletter and fills them
           in the skeleton html template."""
        for val in self.config["newsletter_titles"]:
            if val["language"] == lang:
                titles = val

        for i in titles:
            self.titles[i] = titles[i]


    def fill_titles(self):
        """Fills the title in the skeleton."""
        for i in self.titles:
            if i != "language":
                self.kwp.add_keyword('{{ ' + i + ' }}', self.titles[i])

        self.new_html = self.kwp.replace_keywords(self.skeleton)


    def fill_variable(self, nw, nw_info, nw_file_name, content):
        """Fill variable information."""
        # Fill Main Info
        self.kwp.add_keyword('{{ headline }}', nw['headline'])

        # Date and Page Title
        for index, row in content[0].iterrows():
            if row['AUDIENCE'] == 'ISSUE DATE':
                self.kwp.add_keyword('{{ date }}',
                    self.clean_text(row['VALUE'].strip()))
            else:
                if nw['type'] in row['AUDIENCE']:
                    self.kwp.add_keyword('{{ page_title }}',
                        row['VALUE'].strip())

        # Sets featured and normal articles
        self.set_articles(content[1], nw)

        # Sets Events
        self.set_events(content[2], nw)

        # Sets Quick Links
        self.set_quick_links(content[3], nw)

        # Social Links
        social_html = "templates/snippets/{}_social.html".format(
            nw['region'].lower())
        self.kwp.add_keyword('{{ social }}',
            self.get_file(social_html))

        # Replace variables
        self.new_html = self.kwp.replace_keywords(self.skeleton)


    def set_quick_links(self, content, nw):
        ql_html = ''
        for index, row in content.iterrows():
            if row['AUDIENCE'] == 'All' or row['AUDIENCE'] == nw['tc']:
                ql_html_snip = self.get_file(
                    "templates/snippets/quick_link.html")
                # Replace Quick Links Variables
                if ':' in row['QUICK LINK']:
                    qkl_array = row['QUICK LINK'].split(':')
                    qkl = '<strong>{}</strong>: {}'.format(
                        qkl_array[0][:-1], qkl_array[1].strip())
                else:
                    qkl = row['QUICK LINK']

                self.kwp.add_keyword('{{ quick_link_title }}', qkl)
                self.kwp.add_keyword('{{ quick_link_url }}', row['URL'])
                self.kwp.add_keyword('{{ quick_link_cta }}', row['CTA'])
                ql_html_snip = self.kwp.replace_keywords(ql_html_snip)
                ql_html += ql_html_snip

        self.kwp.add_keyword('{{ quick_links }}', ql_html)
        self.new_html = self.kwp.replace_keywords(self.skeleton)


    def set_events(self, content, nw):
        """Creates the events."""
        event_html = ''
        for index, row in content.iterrows():
            if row['AUDIENCE'] == 'All' or row['AUDIENCE'] == nw['tc']:
                event_html_snip = self.get_file(
                    "templates/snippets/event.html")
                # Replace Event Variables
                self.kwp.add_keyword('{{ event_title }}', row['EVENT'])
                self.kwp.add_keyword('{{ event_date }}', row['DATE'])
                self.kwp.add_keyword('{{ event_location }}', row['LOCATION'])
                self.kwp.add_keyword('{{ event_url }}', row['URL'])
                self.kwp.add_keyword('{{ event_cta }}', row['CTA'])
                event_html_snip = self.kwp.replace_keywords(event_html_snip)
                event_html += event_html_snip

        self.kwp.add_keyword('{{ events }}', event_html)
        self.new_html = self.kwp.replace_keywords(self.skeleton)


    def set_articles(self, content, nw):
        """Set articles."""
        featured = ''
        articles = ''

        featured_x = 0

        # Go over articles
        for index, row in content.iterrows():
            if 'feature' in self.clean_text(row['ARTICLE SME']).lower():
                if row['AUDIENCE'] == 'All' or row['AUDIENCE'] == nw['tc']:
                    featured += self.create_featured(row, featured_x)
                    featured_x += 1
            else:
                if row['AUDIENCE'] == 'All' or row['AUDIENCE'] == nw['tc']:
                    if index < (len(content.index) - 1):
                        sep = True
                    else:
                        sep = False
                    articles += self.create_articles(row, nw, sep)

        self.kwp.add_keyword('{{ featured }}', featured)
        self.kwp.add_keyword('{{ articles }}', articles)
        self.new_html = self.kwp.replace_keywords(self.skeleton)


    def create_articles(self, row, nw, sep):
        """Creates articles."""

        # Category
        cat = self.clean_text(row['IMAGE']).lower()
        if 'tp' in cat:
            html = self.get_file("templates/snippets/article_tp.html")
        else:
            html = self.get_file("templates/snippets/article.html")
            self.kwp.add_keyword('{{ article_category }}', cat)

        # Icons
        icons = self.config['newsletter_icons']
        icon = list(filter(lambda x: x[nw['lang']] == cat, icons))
        if len(icon):
            self.kwp.add_keyword('{{ article_icon }}', icon[0]['url'])
        else:
            msg = 'Correct {} category in {}'.format(row['ARTICLE SME'],
                nw['lang'])
            print(msg)

        # Headline
        self.kwp.add_keyword('{{ article_headline }}', row['HEADLINE'])

        # Copy + Embedded Links
        copy = self.clean_text(row['COPY'])
        emb = self.clean_text(row['EMBEDDED LINKS']).split('LINK: ')
        emb.pop(0)
        if len(emb):
            for em in emb:
                em_arr = em.split('http')
                em_title = self.clean_text(em_arr[0])
                em_link = 'http' + self.clean_text(em_arr[1])
                self.kwp.add_keyword(em_title,
                    self.create_link(em_title, em_link))
            copy = self.kwp.replace_keywords(copy)

        self.kwp.add_keyword('{{ article_copy }}', copy)

        # Ctas
        ctas = self.clean_text(row['CTAS']).split('CTA: ')
        ctas.pop(0)
        cta_html = ''
        for cta in ctas:
            cta_arr = cta.split('http')
            cta_html_snip = self.get_file(
                "templates/snippets/article_cta.html")
            # {{ article_cta_url }}
            self.kwp.add_keyword('{{ article_cta_url }}',
                'http' + cta_arr[1])
            # {{ article_cta_title }}
            self.kwp.add_keyword('{{ article_cta_title }}', cta_arr[0])
            cta_html += self.kwp.replace_keywords(cta_html_snip)

        self.kwp.add_keyword('{{ article_ctas }}', cta_html)

        # Separator
        if sep:
            sep_html = self.get_file(
                "templates/snippets/article_sep.html")
            html += sep_html

        # Replace all
        return self.kwp.replace_keywords(html)


    def create_featured(self, row, index):
        """Create featured article."""
        if index % 2 == 0:
            f_file = "templates/snippets/featured_l.html"
        else:
            f_file = "templates/snippets/featured_r.html"
        html = self.get_file(f_file)

        # Headline
        self.kwp.add_keyword('{{ featured_headline }}', row['HEADLINE'])

        #Embedded Links
        copy = row['COPY']
        emb = self.clean_text(row['EMBEDDED LINKS']).split('LINK: ')
        emb.pop(0)
        if len(emb):
            for em in emb:
                em_arr = em.split('http')
                em_title = self.clean_text(em_arr[0])
                em_link = 'http' + self.clean_text(em_arr[1])
                self.kwp.add_keyword(em_title,
                    self.create_link(em_title, em_link))
            copy = self.kwp.replace_keywords(copy)

        # Copy
        self.kwp.add_keyword('{{ featured_copy }}', copy)

        # Ctas
        ctas = self.clean_text(row['CTAS']).split('CTA: ')
        ctas.pop(0)
        cta_html = ''
        for cta in ctas:
            cta_arr = cta.split('http')
            cta_html_snip = self.get_file(
                "templates/snippets/featured_cta.html")
            # {{ featured_cta_url }}
            self.kwp.add_keyword('{{ featured_cta_url }}',
                'http' + cta_arr[1])
            # {{ featured_cta_title }}
            self.kwp.add_keyword('{{ featured_cta_title }}', cta_arr[0])
            cta_html += self.kwp.replace_keywords(cta_html_snip)

        # cta
        self.kwp.add_keyword('{{ featured_ctas }}', cta_html)
        return self.kwp.replace_keywords(html)


    def create_emails(self, type, nw_info):
        """Create latam emails."""
        files = os.listdir(nw_info['path'])
        status = self.get_file(nw_info['path'] + '/status.txt').strip()
        word_docs = []
        imgs = []
        nws = self.config["newsletter_ref"]

        # Check folder status to avoid duplicate creation
        if status != 'approved':

            # Get LATAM Newsletters
            lanws = list(filter(lambda x: x['region'] == nw_info['region'], nws))

            # Separates Docx and Images
            for file in files:
                if '.docx' in file and '~' not in file:
                    word_docs.append(file)
                else:
                    imgs.append(file)

            # Check if docs are complete
            if all(elem in self.docs  for elem in word_docs):
                for doc in word_docs:

                    # Get Full Doc Path
                    full_doc = '{}/{}'.format(nw_info['path'], doc)
                    # Get Content Tables
                    content = self.wr.get_tables(full_doc)
                    # Fill Content Titles by Language
                    lang = doc[:-5]
                    self.get_titles(lang)
                    self.fill_titles()

                    # Loops over the possible newsletters for LATAM
                    success = True
                    for nw in lanws:
                        if nw['lang'] == lang:

                            # Creates HTML filename
                            nw_name = [
                                nw['name'], nw['type'], nw['country'],
                                nw['region'], nw['lang'], nw_info['nw_code'],
                                nw['code']
                                ]
                            nw_file_name = nw_info['html_path']
                            nw_file_name += '/{}.html'.format('_'.join(nw_name))

                            self.fill_variable(nw, nw_info, nw_file_name, content)

                            # Open and writes the html file
                            nw_html_file = open(nw_file_name, "w")
                            nw_html_file.write(self.new_html)
                            nw_html_file.close()

                            self.new_html = ''

            else:
                self.alert("""
                    \nYou didn't add the three correct
                    word docs in the LATAM folder {}
                """.format(nw_info['nw_code']))
        else:
            self.alert('The {} for {} is approved!'.format(
                nw_info['nw_code'], nw_info['region']), 'success')
