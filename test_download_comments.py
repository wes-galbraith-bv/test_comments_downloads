from random import random
import os

import requests
import pytest
import pandas as pd
import xlrd



def make_request(database, primary_key=None, unique_id=None, query=None):
    base_url = f"http://localhost:5000/data/comments/{database}/download"
    headers = {
        'Content-Type': "application/json",
        'Authorization': "Bearer b3c3b5b8-90a8-465d-9235-9e231c5cba60",
        'User-Agent': "PostmanRuntime/7.15.2",
        'Accept': "*/*",
        'Cache-Control': "no-cache",
        'Postman-Token': "a0fa2f71-fa78-49b4-9efc-de84b894b9ec,f69e87d1-71f5-4102-98cc-fa88a64c3eb1",
        'Host': "test-geotrak-service.myloadspring.com",
        'Accept-Encoding': "gzip, deflate",
        'Content-Length': "287",
        'Connection': "keep-alive",
        'cache-control': "no-cache"
    }
    payload = {}
    if primary_key is not None:
        payload['primaryKey'] = primary_key
    if unique_id is not None:
        payload['uniqueId'] = unique_id
    if query is not None:
        payload['query'] = query

    response = requests.get(base_url, params=payload, headers=headers)
    return response


def check_headers(response):
    assert response.headers.filetype

def get_xlsx(response):
    wb = xlrd.open_workbook(file_contents=response.content)
    df = pd.read_excel(wb)
    return df


def check_column_names(df):
    valid_names = {'CommentId', 'SiteId', 'CommentType', 'Comment', 'Created', 'CreatedBy'}
    assert set(df.columns) == valid_names


def test_valid_site_id():
    response = make_request('V3_Turf', primary_key='SiteId', unique_id=('70572'))
    df = get_xlsx(response)
    assert response.status_code == 200
    # df.to_excel('./data/test_valid_site_id.xlsx', index=False)
    check_column_names(df)


def test_invalid_site_ids():
    for id in ('jaberwocky'):
        response = make_request('V3_Turf', unique_id=(id))
        assert response.status_code == 400


def test_empty_site_id():
    response = make_request('V3_Turf', unique_id=())
    assert response.status_code == 400


def test_valid_query():
    response=make_request('V3_Turf', unique_id=('70572'), query="CommentType='Type A'")
    assert response.status_code == 200
    df = get_xlsx(response)
    assert df.loc[0, 'CommentType'] == 'Type A'
    assert len(df) == 1
    # df.to_excel('./data/test_valid_query.xlsx')


def test_invalid_query():
    response=make_request('V3_Turf', unique_id=('70572'), query="CommentType=Type C")
    assert response.status_code == 400


def test_invalid_primary_key():
    response = make_request('V3_Turf', primary_key='OBJECTID', unique_id=('70572'))
    assert response == 400




if __name__ == '__main__':
    response = make_request('V3_Turf', unique_id=('70572'))
    df = get_xlsx(response)
