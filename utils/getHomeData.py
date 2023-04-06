from .utils import *
import pandas as pd


def getHomeData():
   df['number_of_applicants'] = df['number_of_applicants'].astype(int)
   df['number_of_recruits'] = df['number_of_recruits'].astype(int)
   df['number_of_position'] = df['number_of_position'].astype(int)

   sum_applicants = df['number_of_applicants'].sum()
   sum_recruits = df['number_of_recruits'].sum()
   sum_position= df['number_of_position'].sum()
   rate= df["number_of_recruits"].sum() / df["number_of_applicants"].sum()
   rate = round(rate, 3)


   return sum_applicants,sum_recruits,rate,sum_position

getHomeData()
