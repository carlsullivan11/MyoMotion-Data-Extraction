from genericpath import isdir
import re
import numpy as np
import os
import pandas as pd


def initialContactExtract(df):
    df = pd.DataFrame(df)

    # Checks 'Fz RT,N' and 'Fz LT,N' column to find which foot stepped down (measured in N) 
    if(df['Fz RT,N'].max() > df['Fz LT,N'].max()):  
        df = df.drop('Fz LT,N', axis=1)             # Drops uneeded force column
        df = df[df['Fz RT,N'] >= 10] # Drops all columns where force is > 10N

        dropList = []                               # dropList collects the columns with 'LT,deg' to be dropped at the end of the for loop
        for col in df.columns:
            colSplit = col.split(' ')
            if('Pelvic' not in colSplit):           # Keeps all 'Pelvic' values 
                if('LT,deg' in colSplit):           # Adds all 'LT,deg' values to dropList
                    dropList.append(col)
            
        df = df.drop(dropList, axis=1)              # Drop all 'Lt,deg' columnss except for any pelvic columns

    else:
        df = df.drop('Fz RT,N', axis=1)             # Drops uneeded force column
        df = df[pd.to_numeric(df['Fz LT,N']) >= 10] # Drops all columns where force is > 10N

        dropList = []
        for col in df.columns:
            colSplit = col.split(' ')
            if('Pelvic' not in colSplit):
                if('RT,deg' in colSplit):
                    dropList.append(col)
            
        df = df.drop(dropList, axis=1)

    df = df.iloc[[0]]
    return df # returns initial contact row of df

def calcAverage(df):
    df = pd.DataFrame(df)
    # groups them by trial then computes the average of each column
    avgDF = df.groupby('File Name').mean()
    #print(avgDF.head())

    return avgDF

def singleRowWrite(df, testSubject, colName, index):                          
    
    
    df = pd.DataFrame(df)
    f = open('singleColumnExtraction.csv', 'a')
    f.write(df.to_csv())


def changeColmNames(df, testSubject):
    df = pd.DataFrame(df)
    writeDF = pd.DataFrame()
    
    print(df.head())
    for row in range(df.shape[0]):
        tempDF = df.iloc[[row]]
        #print(tempDF.head())
        for col in tempDF.columns:
            colTemp = re.split(' |,', col)
            colTemp.insert(0, tempDF.index[0])
            colTemp = '_'.join(colTemp)
            #print(colTemp)
            tempDF = tempDF.rename(columns={col:colTemp})

        if(writeDF[1] == 0):
            writeDF = tempDF
        else:
            writeDF = writeDF.join(tempDF)


    print(writeDF.head(76).transpose())
    return df




def main():
    #folder = input('Please enter folder name: ')
    folder = 'TestSubjects'
    filedict = {'File Name': []}                    # Used to gather the names of the file to join to the values DF
    tempdf = pd.DataFrame()                         # Used to collect desired row for each file. Only needed when using SingleColumnWrite


    for testSubject in os.listdir(folder):
        testSubject = os.path.join(folder, testSubject)
        #print(testSubject)

        if os.path.isdir(testSubject):
            for fileName in os.listdir(testSubject):             # Searches through desired folder for all files in folder
                file = os.path.join(testSubject, fileName)       
                #print(file)

                if os.path.isfile(file):
                    title = file.title().split('.')
                    if(title[1] == 'Csv'):
                        print('CSV: ', title[0])

                        trialFileName = title[0].split('/')
                        appendFileName = trialFileName[2]
                        filedict['File Name'].append(appendFileName[:-1])

                        # Read CSV and create new DF, Extracts out Force & Columns partaining to Deg, appends those two DF to new DF
                        df = pd.read_csv(file, low_memory=False, header=3)
                        force_df = df[['Fz RT,N','Fz LT,N']]
                        values_df = df.loc[:,'Hip Flexion LT,deg':'Foot Rotation Ext RT,deg']
                        df = force_df.join(values_df)

                        # Extract IC row from DF, saves to DF
                        df = initialContactExtract(df)
                        
                        # DF after IC has been extracted
                        print(df.head())

                        #creates tempdf to append each trial to after extraction
                        if(tempdf.shape[0] == 0):
                            tempdf = df
                        else:
                            tempdf = pd.concat([tempdf, df], ignore_index = True)
            
            #creates a df for each file name
            filedf = pd.DataFrame(filedict)

            # joins the file DF to the temp DF
            df = filedf.join(tempdf)

            #print(df.head(12))
            avgDF = calcAverage(df)

            # Change Column Names
            df = changeColmNames(avgDF, trialFileName[1])

            #singleColumnWrite(df)

main()
            
            

"""
*******************************
******UNUSED FUNCTIONS********* 
*******************************

"""


def multipleCoumnWrite(df, title):                  # Writes each file with seperate columns. Could be used if Right and Left leg is used in a folder
    df = pd.DataFrame(df)
    df = df.iloc[[0]]
    
    f = open('extractedData.csv', 'a')
    f.write((title[0]) + (df.shape[1] * ',') + '\n') 
    f.write(df.to_csv())
            

def maxContactExtract(df):
    df = pd.DataFrame(df)
    
    if(df['Fz RT,N'].max() > df['Fz LT,N'].max()):  # Checks 'Fz RT,N' and 'Fz LT,N' column to find which foot stepped down (measured in N)
        df = df.drop('Fz LT,N', axis=1)             # Drops uneeded force column
        df = df[pd.to_numeric(df['Fz RT,N']) == df['Fz RT,N'].max()] # Finds max N in df and returns that row

        dropList = []                               # dropList collects the columns with 'LT,deg' to be dropped at the end of the for loop
        for col in df.columns:
            colSplit = col.split(' ')
            if('Pelvic' not in colSplit):           # Keeps all 'Pelvic' values 
                if('LT,deg' in colSplit):           # Adds all 'LT,deg' values to dropList
                    dropList.append(col)
            
        df = df.drop(dropList, axis=1)              # Drop all 'Lt,deg' columnss except for any pelvic columns

    else:
        df = df.drop('Fz RT,N', axis=1)             # Drops uneeded force column
        df = df[pd.to_numeric(df['Fz LT,N']) == df['Fz LT,N'].max()] # Finds max N in DF and returns that row

        dropList = []
        for col in df.columns:
            colSplit = col.split(' ')
            if('Pelvic' not in colSplit):
                if('RT,deg' in colSplit):
                    dropList.append(col)
            
        df = df.drop(dropList, axis=1)
    
    return df # Returns max row of DF
