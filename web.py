#!/usr/bin/env python3

import sqlite3
import json
import copy
from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request

from common import PROPERTY_TYPES_2
from common import SystembolagetProperty
from common import PropertyType
from common import get_property_by_identifier
from common import format_value
from systembolaget_parser import get_url

app = Flask(__name__)


def parse_int(s: str, default: int):
    try:
        return int(s)
    except TypeError:
        return default


@app.route('/')
def get_index():
    # TODO add type_name
    prop_types = copy.deepcopy(PROPERTY_TYPES_2)
    prop_types.append(SystembolagetProperty('url', PropertyType.URL, 'URL', True))

    for p in prop_types:
        p.type = p.type.name

    return render_template('index.html', columns=prop_types)


@app.route('/category/<string:category_identifier>')
def get_category(category_identifier):
    connection = sqlite3.connect('sortiment.db')
    cur = connection.cursor()

    prop = get_property_by_identifier(category_identifier)
    if not prop or prop.type != PropertyType.CATEGORY:
        return jsonify([])

    # Todo: Possible future SQL injection
    q = cur.execute('SELECT DISTINCT {category} FROM sortiment WHERE '
                    '{category} IS NOT NULL'
                    .format(category=prop.identifier))
    filter_list = {}
    for row in q:
        filter_list[row[0]] = row[0]

    connection.close()
    return jsonify(filter_list)


@app.route('/items')
def get_items():
    offset = parse_int(request.args.get('offset'), 0)
    limit = parse_int(request.args.get('limit'), -1)

    sort = request.args.get('sort')
    prop = get_property_by_identifier(sort)
    if not prop:
        sort = PROPERTY_TYPES_2[0].identifier

    order = 'DESC' if request.args.get('order') == 'desc' else 'ASC'

    request_filter = {}
    if 'filter' in request.args:
        try:
            request_filter_input = json.loads(request.args.get('filter'))
        except json.JSONDecodeError:
            request_filter_input = {}

        if type(request_filter_input) != dict:
            request_filter_input = {}

        for category, identifier in request_filter_input.items():
            prop = get_property_by_identifier(category)
            if not prop or prop.type != PropertyType.CATEGORY:
                continue

            request_filter[category] = identifier

    search = request.args.get('search', '')
    search = ''.join([c for c in search if c.isalnum()])

    # Create where clause
    where_filter_expressions = []
    if request_filter:
        # Todo: Possible future SQL injection
        where_filter_expressions = ["{}='{}'".format(name, value) for name, value in request_filter.items()]

    where_search_expressions = []
    if search:
        # Todo: Possible future SQL injection
        if search.isdigit():
            # Might be identifier
            where_search_expressions.append("nr = '{}'".format(search))
            where_search_expressions.append("Artikelid = '{}'".format(search))
            where_search_expressions.append("Varnummer = '{}'".format(search))

        # Todo: This search method might be slow
        where_search_expressions.append("Namn LIKE '%{}%'".format(search))
        where_search_expressions.append("Namn2 LIKE '%{}%'".format(search))

    where_clause = ''
    if where_filter_expressions or where_search_expressions:
        where_clause = 'WHERE '
        where_clause += ' AND '.join(where_filter_expressions)
        where_clause += ' OR '.join(where_search_expressions)

    # Connect to database
    connection = sqlite3.connect('sortiment.db')
    cur = connection.cursor()

    # Count records
    cur.execute('SELECT COUNT(*) FROM sortiment {}'.format(where_clause))
    total_records = cur.fetchone()[0]

    # Grab records
    # Todo: Possible future SQL injection
    query_str = ('SELECT * FROM sortiment {} ORDER BY {} {} LIMIT {} OFFSET {}'
                 .format(where_clause, sort, order, limit, offset))
    q = cur.execute(query_str)

    data = []
    for row in q:
        row_data = {}
        for raw_value, p in zip(row, PROPERTY_TYPES_2):
            value = format_value(raw_value, p.type)

            row_data[p.identifier] = value

        row_data['url'] = get_url(row_data['nr'], row_data['Varugrupp'],
                                  row_data['Namn'])
        data.append(row_data)

    response = {
        'total': total_records,
        'rows': data,
    }

    connection.close()

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
