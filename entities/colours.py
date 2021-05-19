import logging
import datetime
import pandas as pd
from .db_helper import DBHelper
from .webutils import WebUtils


class Colours(DBHelper):

    def __init__(self, context, reload=False):
        super(Colours, self).__init__(context,
                                      'cColours',
                                      {'id': {'type': 'TEXT', 'value': '', 'other': 'NOT NULL PRIMARY KEY'},
                                       'name': {'type': 'TEXT', 'value': '', 'other': ''},
                                       'hex': {'type': 'TEXT', 'value': '', 'other': ''},
                                       'year_range': {'type': 'TEXT', 'value': '', 'other': ''},
                                       'category': {'type': 'TEXT', 'value': '', 'other': ''},
                                       'sync_dt_tm': {'type': 'TEXT', 'value': '', 'other': ''}})
        self.context = context

    def sync_with_bricklink(self):
        logging.info("    [+] Colours: Load From Web")
        body = self.context.wu.get_content('https://www.bricklink.com/catalogColors.asp?utm_content=subnav')
        titles = ['Solid Colors', 'Transparent Colors', 'Chrome Colors', 'Pearl Colors', 'Satin Colors',
                  'Metallic Colors', 'Milky Colors', 'Glitter Colors', 'Speckle Colors', 'Modulex Colors']
        colour_list = pd.DataFrame()
        for title in titles:
            html_table = WebUtils.get_table_after(body, title)
            clrs = WebUtils.html_table_to_df(html_table)
            clrs['category'] = title
            colour_list = pd.concat([colour_list, clrs])

        colour_list['sync_dt'] = datetime.datetime.now().strftime('%Y-%m-%d')
        colour_list[1] = colour_list[1].apply(WebUtils.strip_html)
        colour_list[2] = colour_list[2].apply(WebUtils.get_bgcolour)
        colour_list[4] = colour_list[4].apply(WebUtils.strip_html)
        colour_list[9] = colour_list[9].apply(WebUtils.strip_html)
        colour_list = colour_list.drop(columns=[3, 5, 6, 7, 8])
        colour_list = colour_list.rename(columns={1: 'bricklink_id', 2: 'hex', 4: 'name', 9: 'year_range'})
        for index, row in colour_list.iterrows():
            logging.info('        [-] Saving Colour: {}'.format(row['name']))
            self.context.execute('DELETE from colour where id = {};'.format(row['bricklink_id']))
            self.context.execute(
                'INSERT INTO colour (id, name, hex, year_range, category, sync_dt_tm) VALUES({}, "{}", "{}", "{}", "{}", "{}");'.format(
                    row['bricklink_id'], row['name'], row['hex'], row['year_range'], row['category'], row['sync_dt']))
        self.context.execute('update colour set red = CONV(substring(hex,1,2), 16, 10), green = CONV(substring(hex,3,2), 16, 10), blue = CONV(substring(hex,5,2), 16, 10) WHERE 1')
        logging.info('        [-] Colour Sync Complete.')

    def get_colour_by_name(self, colour_name):
        return self.get_by_name(colour_name)

    def get_colour_by_id(self, colour_id):
        return self.get_by_id(colour_id)

    def get_map(self):
        colour_map = {}
        db_results = self.context.query('SELECT * FROM Colours ;')
        for x in range(len(db_results)):
            td = self.dict_from_itter(db_results[x])
            colour_map[td['id']] = td
        return colour_map
