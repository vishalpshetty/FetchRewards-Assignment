#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 16:36:40 2021

@author: vishalpattanshetty
"""
import pandas as pd
import json

#This is a function to read the files
def readFiles(filename):
    with open(filename) as f:
        lines = f.readlines()
    df = []
    for line in lines:
        df.append(json.loads(line))
    return df

brands = readFiles('/Users/vishalpattanshetty/Downloads/brands.json')
receipts = readFiles('/Users/vishalpattanshetty/Downloads/receipts.json')
users = readFiles('/Users/vishalpattanshetty/Downloads/users.json')

#Users and brands json files are normalized, receipts has more complicated structure will be looked later in the script.
usersdf = pd.json_normalize(users,max_level=1)
brandsdf = pd.json_normalize(brands,max_level=2)



#Renaming columns to readable names for brands file
brandsdf.rename(columns={'_id.$oid': 'brand_id', 'cpg.$id.$oid': 'cpgOid', 'cpg.$ref': 'cpgRef'}, inplace=True)

#Data Quality check #1
#Dropping duplicate keys for brand_id
brandsdf = brandsdf.drop_duplicates(subset='brand_id').reset_index(drop=True)
brandsdf.to_csv('/Users/vishalpattanshetty/Downloads/brands_clean.csv',index=False)

#Renaming columns to readable names for users file
usersdf.rename(columns={'_id.$oid': 'user_id', 'createdDate.$date': 'createdDate', 'lastLogin.$date': 'lastLogin'}, inplace=True)
usersdf['createdDate'] = pd.to_datetime(usersdf['createdDate']/1000,unit='s')
usersdf['lastLogin'] = pd.to_datetime(usersdf['lastLogin']/1000,unit='s')

usersdf.to_csv('/Users/vishalpattanshetty/Downloads/users_clean.csv',index=False)

#Normalizing receipts file
receiptsdf = pd.json_normalize(receipts)
receiptsdfOriginal = receiptsdf.drop(['rewardsReceiptItemList'], axis=1)
receiptsdfOriginal.rename(columns={'_id.$oid': 'receipt_id', 'createDate.$date': 'createDate', 'pointsAwardedDate.$date': 'pointsAwardedDate'}, inplace=True)
receiptsdfOriginal['createDate'] = pd.to_datetime(receiptsdfOriginal['createDate']/1000,unit='s')
receiptsdfOriginal['pointsAwardedDate'] = pd.to_datetime(receiptsdfOriginal['pointsAwardedDate']/1000,unit='s')
receiptsdfOriginal.drop(['dateScanned.$date', 'finishedDate.$date',
       'modifyDate.$date','purchaseDate.$date'], axis=1,inplace=True)

receiptsdfOriginal.to_csv('/Users/vishalpattanshetty/Downloads/receipts_clean.csv',index=False)

#Processing the rewardsReceiptItemList- extracting info from this field as new CSV file
#Adding non-null values for barcode and description fields
[item.update({'rewardsReceiptItemList':[{'barcode':None,'description':None}]}) for item in receipts if 'rewardsReceiptItemList' not in item.keys()]

#Normalizing the ReceiptItemList data
ReceiptItemList_df = pd.json_normalize(receipts, record_path='rewardsReceiptItemList',meta=[["_id","$oid"]])
ReceiptItemList_df.rename(columns={'_id.$oid': 'receipt_id'}, inplace=True)
#keeping columns I need
ReceiptItemList_df = ReceiptItemList_df[['receipt_id','barcode','description','finalPrice','itemPrice','brandCode']]

ReceiptItemList_df.to_csv('/Users/vishalpattanshetty/Downloads/receiptsItemList_clean.csv')


