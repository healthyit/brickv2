import logging
import urllib.request
import urllib.parse
from collections import OrderedDict
import pandas as pd
from bs4 import BeautifulSoup
import datetime
import time


class WebUtils(object):

    delay_sec = 0

    def __init__(self):
        logging.info("    [+] WebUtils: Init")
        self.last_download = datetime.datetime.now() - datetime.timedelta(days=1)
        self.cookies = {}

    def save_cookies(self, response):
        for header in response.headers._headers:
            if header[0] == 'Set-Cookie':
                # /<class 'tuple'>: ('Set-Cookie', 'BLNEWSESSIONID=2E122B16C88A6405C1B9AA7837B3AE6D;Path=/;Domain=bricklink.com;Secure;HttpOnly')
                pos1 = header[1].find("=")
                key = header[1][0:pos1]
                if not self.cookies.get(key, None):
                    self.cookies[header[1][0:pos1]] = header[1][pos1+1:]

    @staticmethod
    def strip_html(html_text):
        soup = BeautifulSoup(html_text, 'html.parser')
        return (soup.get_text()).strip()

    @staticmethod
    def urlencode(inputstr):
        return urllib.parse.quote(inputstr)

    def get_content(self, url, method='GET', idenified=False, data=None):
        logging.info('                            [-] Download Loading: {}'.format(url))
        if (datetime.datetime.now()-self.last_download).total_seconds() < WebUtils.delay_sec:
            logging.info("                            [-] WebUtils: Sleeping for {} seconds".format(WebUtils.delay_sec))
            time.sleep(WebUtils.delay_sec)
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0'})
        if idenified:
            req.add_header("Cookie", "BLNEWSESSIONID={}".format(self.cookies['BLNEWSESSIONID'].split(';')[0]))
        if data:
            data = urllib.parse.urlencode(data)
            data = data.encode('ascii')
            try:
                response = urllib.request.urlopen(req, data=data)
            except:
                logging.info('Download error, waiting 60 seconds to retry')
                time.sleep(60)
                response = urllib.request.urlopen(req, data=data)
        else:
            try:
                response = urllib.request.urlopen(req)
            except Exception as e:
                logging.info('Download error, waiting 60 seconds to retry: {}'.format(e))
                time.sleep(60)
                response = urllib.request.urlopen(req)

        self.save_cookies(response)
        body = response.read()
        self.last_download = datetime.datetime.now()
        logging.info('                            [-] Download Complete ')
        html = body.decode("utf-8")
        with open('last.html', 'w') as the_file:
            the_file.write(html)
        return html

    @staticmethod
    def get_table_after(body, title):
        pos = body.find(title)
        pos = body.find('<TABLE', pos)
        pos = body.find('<CENTER>', pos)
        table_start = body.find('<TABLE', pos)
        table_end = body.find('</TABLE>', table_start)
        table = body[table_start:(table_end+8)]
        return table

    @staticmethod
    def get_between(txt, start_text, end_text, start_at=0, inclusive=False, aggressive=False):
        pos1 = txt.find(start_text, start_at)
        if aggressive:
            pos2 = txt.find(end_text, pos1+len(start_text))
        else:
            pos2 = txt.rfind(end_text)
        if inclusive:
            return txt[pos1:(pos2+len(end_text))]
        else:
            return txt[(pos1+len(start_text)):pos2]

    @staticmethod
    def get_bgcolour(html_txt):
        return WebUtils.get_between(html_txt, 'BGCOLOR="', '"', 0, False, True)

    @staticmethod
    def get_strong(html_txt):
        return WebUtils.get_between(html_txt, '<strong>', '</strong>', 0, False, True)

    @staticmethod
    def get_img_src(html_txt):
        pos = html_txt.find('<IMG')
        return WebUtils.get_between(html_txt, "SRC='", "'", pos, False, True)

    @staticmethod
    def get_link(html_txt):
        pos = html_txt.find('<A')
        return WebUtils.get_between(html_txt, 'HREF="', '"', pos, False, True)

    @staticmethod
    def get_link_text(html_txt):
        pos = html_txt.find('<A')
        return WebUtils.get_between(html_txt, '>', '</A>', pos, False, True)

    @staticmethod
    def html_table_to_df(html_table, mode=0, header_row=True): #mode 0:full Cell 1:Inner HTML 2:Inner No Html 3:
        results = []

        row_cnt = 0
        row_pos = html_table.find('<TR')
        while row_pos > -1:  # ROWS
            row = OrderedDict()
            row_pos_end = html_table.find('</TR>', row_pos)
            row_text = html_table[row_pos:row_pos_end+5]
            if row_cnt > 0 or not header_row:
                col_pos = row_text.find('<TD')
                col_cnt = 1
                while col_pos > -1:
                    col_pos_end = row_text.find('</TD>', col_pos)
                    full = row_text[col_pos:col_pos_end+5]
                    inner = WebUtils.get_between(full, '>', '<')
                    # stripped = (BeautifulSoup(inner)).get_text(features="html.parser")
                    # decoded = BeautifulSoup(stripped, convertEntities=BeautifulSoup.HTML_ENTITIES)
                    # if mode == 1:
                    #     row[col_cnt] = inner
                    # elif mode == 2:
                    #     row[col_cnt] = decoded
                    # else:
                    row[col_cnt] = full
                    col_pos = row_text.find('<TD', col_pos + 1)
                    col_cnt = col_cnt + 1
                results.append(row)
            row_cnt = row_cnt + 1
            row_pos = html_table.find('<TR', row_pos+1)

        return pd.DataFrame(results)



