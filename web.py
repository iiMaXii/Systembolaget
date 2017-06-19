#!/usr/bin/env python3

import sqlite3
import json
import copy
from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request


import systembolaget_parser

app = Flask(__name__)


def parse_int(s: str, default: int):
    try:
        return int(s)
    except TypeError:
        return default


@app.route('/')
def get_index():
    # TODO maybe add URL to PROPERTY_TYPES_2
    # TODO add type_name
    prop_types = copy.deepcopy(systembolaget_parser.PROPERTY_TYPES_2)
    prop_types.append(systembolaget_parser.SystembolagetProperty('url', systembolaget_parser.PropertyType.URL, 'URL', True))

    for p in prop_types:
        p.type = p.type.name

    return render_template('index.html', columns=prop_types)


@app.route('/category/<string:category_identifier>')
def get_category(category_identifier):
    connection = sqlite3.connect('sortiment.db')
    cur = connection.cursor()

    prop = systembolaget_parser.get_property_by_identifier(category_identifier)
    if not prop or prop.type != systembolaget_parser.PropertyType.CATEGORY:
        return jsonify([])

    # Todo: Possible future SQL injection
    q = cur.execute('SELECT ID, Name FROM kategori_{}'.format(category_identifier))
    filter_list = {}
    for row in q:
        filter_list[int(row[0])] = row[1]  # int() unnecessary?

    connection.close()

    return jsonify(filter_list)


@app.route('/items')
def get_items():
    offset = parse_int(request.args.get('offset'), 0)
    limit = parse_int(request.args.get('limit'), -1)
    sort = request.args.get('sort')

    prop = systembolaget_parser.get_property_by_identifier(sort)
    if not prop:
        sort = systembolaget_parser.first(systembolaget_parser.PROPERTY_TYPES_2).identifier

    order = 'desc' if request.args.get('order') == 'desc' else 'asc'

    request_filter = {}
    if 'filter' in request.args:
        try:
            request_filter_input = json.loads(request.args.get('filter'))
        except json.JSONDecodeError:
            request_filter_input = {}

        if type(request_filter_input) != dict:
            request_filter_input = {}

        for category, identifier in request_filter_input.items():
            if category not in systembolaget_parser.PROPERTY_TYPES.keys() or systembolaget_parser.PROPERTY_TYPES[category] != systembolaget_parser.PropertyType.CATEGORY:
                continue

            request_filter[category] = identifier

    connection = sqlite3.connect('sortiment.db')
    cur = connection.cursor()

    cols = []
    tables = ['sortiment']

    for p in systembolaget_parser.PROPERTY_TYPES_2:
        if p.type == systembolaget_parser.PropertyType.CATEGORY:
            cols.append('kategori_{}.Name'.format(p.identifier))
            tables.append('JOIN kategori_{} ON kategori_{}.ID = sortiment.{}'.format(p.identifier, p.identifier, p.identifier))
        else:
            cols.append('sortiment.{}'.format(p.identifier))

    # Todo: Possible future SQL injection
    where_clause = ''
    if request_filter:
        # Todo: Possible future SQL injection
        where_clause += ' WHERE '
        where_clause += ' AND '.join(['{} = {}'.format(name, value) for name, value in request_filter.items()])

    # Count records
    cur.execute('SELECT COUNT(*) FROM sortiment {}'.format(where_clause))
    total_records = cur.fetchone()[0]

    # Grab records
    print(cols)
    query_str = 'SELECT {} FROM {} {} ORDER BY {} {} LIMIT {} OFFSET {}'.format(', '.join(cols), ' '.join(tables), where_clause, sort, order, limit, offset)
    print(query_str)
    q = cur.execute(query_str)

    data = []
    for row in q:
        row_data = {}
        for raw_value, p in zip(row, systembolaget_parser.PROPERTY_TYPES_2):
            value = systembolaget_parser.format_value(raw_value, p.type)

            row_data[p.identifier] = value

        row_data['url'] = systembolaget_parser.get_url(row_data['nr'],
                                                       row_data['Varugrupp'],
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
