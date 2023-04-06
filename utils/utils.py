import pandas as pd
import pymysql
from flask import render_template
from sqlalchemy import create_engine, engine


con = create_engine('mysql+pymysql://root:991109@localhost:3306/fb')

df = pd.read_sql('select * from result_gk',con=con)

# def typelist(type):
#     type = df[type].values
#     type = list(map(lambda x:x.split(','),type))
#     typelist = []
#     for i in type:
#         for j in i:
#             typelist.append(j)
#     return typelist





