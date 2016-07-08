#!/usr/bin/env python
# coding:utf-8

import itunes_api
import json

api = itunes_api.ItunesApi()
print json.dumps(api.search_by_upc('720642462928', 'My Name Is Jonas'))