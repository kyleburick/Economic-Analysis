import pandas as pd
import numpy as np
from urllib import request
import os
import time
import datetime as dt
import shutil
from tqdm import tqdm
from io import StringIO

"""
This is a package called NasdaqTraderScraper. On the NasdaqTrader website,
there is great day-by-data on numerous stocks, but the file formats and their
storage system of thousands of individual datasets describing each listed
stock on that day make this data impossible to download and work wiht by hand.
This package automates the process of creating a library, downloading, and
updating this data to an easily usable format.

This database can be found at the url:
    'ftp://ftp.nasdaqtrader.com/Files/crosses/'

You only really need to use methods labeled with [Consumer Use]
"""

def set_path(path):
    """
    This sets the directory that your code is running in so you can easily
    open and save files at your desired location.

    path:
        Description: The path to your desired directory
        D-type: String
        Notes: use '/', not '\'
    """
    os.chdir(path)

def clear_folder(folder_path):
    """
    This allows you to choose a directory and delete any files or folders
    saved within it.

    folder_path:
        Description: The path to your desired directory
        D-type: String
        Notes: use '/', not '\'
    """
    #list of strings of all file names
    for the_file in os.listdir(folder_path):
        #creates the path to that file
        file_path = os.path.join(folder_path, the_file)
        try:
            #delete if it's a file
            if os.path.isfile(file_path):
                os.unlink(file_path)
            #delete if it's a folder
            elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

def determine_format(dataframe):
    """
    The database we are scraping data from uses two slightly different data
    formats this determines which format it is using, so we will know how to
    properly format and clean the data.

    dataframe:
        Description: The dataframe you wish to know the format of
        D-type: Pandas.Dataframe

    Notes: This is a very basic way of determining a format and it may
           recognize a new format as an existing format if there is a
           format change, but there hasn't been a new format since 2010, so
           I would nor worry.
    """
    num_columns = len(dataframe.columns) #gets number of columns in dataframe

    if num_columns == 6: #if there are 6 it is the old format
        return 'old'
    elif num_columns == 7: #if there are 6 it is the new format
        return 'new'
    else:
        print('Unrecognized Format...')
        time.sleep(4)

def dates_between(start, end):
    """
    Returns a list of all dates between a start date and an end date including
    leap years.

    start and end:
        Description: The function creates a list of all dates between these
                     two (inclusive)
        D-type: String
        Notes: in the format yyyymmdd
    """
    yrs = [] #initiates a list to store our years
    first_year = int(start[:4]) #the first year we want
    last_year = int(end[:4]) #the last year we want

    #appends each year onto yrs that we want included
    for i in range(first_year, last_year + 1):
        yrs.append(str(i))

    #each month in the mm format
    mos = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', \
           '12']

    def is_leap_year(year):
        """
        Given a year after 2007, this will determine if it is a leap year.

        year:
            Description: The year you want to know about
            D-type: String
            Notes: in the format yyyy
        """
        answer = False

        first_leap = 2008 #2008 was a leap year

        #iterate through leap years until you pass the desired year
        while str(first_leap) <= year:
            #if your hit your chosen year, change the answer to True
            if int(year) == first_leap:
                answer = True
            first_leap += 4
        return answer

    def lst_days(month, year):
        """
        This program will return a list of days in the dd format that there
        will be in that month, including leap years.

        year and month:
            Description: the month and year you wish to know about
            D-type: String
            Notes: in the format yyyy and mm
        """
        #dictionary how many days are commonly in each month (not counting leap)
        days_per_month = {'01': 31, '02': 28, '03': 31, '04': 30, \
                          '05': 31, '06': 30, '07': 31, '08': 31, \
                          '09': 30, '10': 31, '11': 30, '12': 31}
        num_days = days_per_month[month] #dictionary finds amount of days

        #if it is february and a leap year, app an extra day to the number
        if (month == '02') and (is_leap_year(year)):
            num_days = 29

        #compiles a list of days in that month in the dd format
        days = []
        for i in range(1, num_days + 1):
            days.append('0' + str(i) if i < 10 else str(i))

        return days

    #compiles a list of dates between your chosen years in the yyyymmdd format
    dates = []
    for i in yrs:
        for j in mos:
            days = lst_days(j, i)
            for k in days:
                num = i + j + k
                if (num >= start) and (num <= end):
                    dates.append(num)
    return dates

def last_date_downloaded(file_path):
    """
    This will determine how up to date your data is by finding the last date
    that you updated your data.

    file_path:
        Description: the path to your main library
        D-type: String
        Notes: Make sure to use '/', not '\' and that this is to your root
               directory for your data, not the 'individualData' file.
    """
    files = os.listdir(file_path + '/individualData') #list of files in folder
    if len(files) == 0:
        return None
    else:
        dates = [i[10:18] for i in files] #compiles dates from the file names
        return max(dates) #finds last date downloaded

def download_file_information(url):
    """
    This returns the raw data from the url in the form of a list of rows.

    url:
        Description: the url of the file you wish to download
        D-type: String
    """
    file_open = request.urlopen(url) #open the file under that url
    file_info = file_open.read() #reads the file information
    str_info = str(file_info) #converts info to a string
    x = str_info.split("\\n") #splits the string to a list of each row
    return x

def download_csv(file_info, file_path):
    """
    This will interpret the raw file information and download it into your
    directory as a cleaned csv file.

    file_path:
        Description: the path to your main library
        D-type: String
        Notes: Make sure to use '/', not '\' and that this is to your root
               directory for your data, not the 'individualData' file.
    file_info:
        Description: the raw file information
        D-type: String
    """
    df = pd.read_csv(StringIO('\n'.join(file_info))) #reads raw data as csv
    file_format = determine_format(df) #determines the format of the file
    length = len(df)

    #if it is the old format, clean the dataset accordingly
    if file_format == 'old':
        df[df.columns[5]] = df[df.columns[5]].str[:-2]
        df = df.rename(columns = {df.columns[5]: 'IntradayCross', \
             df.columns[0]: 'Date'})
        df = df.drop([0, length - 1, length - 2, length - 3])
    #if it is the new format, clean the dataset accordingly
    elif file_format == 'new':
        df = df.drop(df.columns[6], axis = 1).drop([0, length - 1, length - 2])
        df = df.rename(columns = {df.columns[0]: 'Date'})
    else:
        print('Invalid format type.')
        time.sleep(1)
        print('This file will not be properly formatted before saving...')
        time.sleep(4)

    df['Date'] = df['Date'].str[6:] + df['Date'].str[:2] + df['Date'].str[3:5]

    df.to_csv(file_path, index = False)

def data_downloader(file_path, start = '20080101', end = None, new_lib = False):
    """
    [Consumer Use]

    This is a tool used to download individual datasets to the 'individualData'
    folder of your library.

    file_path:
        Description: the path to your main library
        D-type: String
        Notes: Make sure to use '/', not '\' and that this is to your root
               directory for your data, not the 'individualData' file.

    start and end:
        Description: the beginning and ending dates for data you want to
                     download (inclusive)
        D-type: String
        Notes: yyyymmdd format

    new_lib:
        Description: whether or not you want your library to start from scratch
        D-type: Boolean
        Notes: if True, delets all files and folders in the given directory
    """
    #if the you do not choose an end data, it will set to the current date
    if end == None:
        end = dt.datetime.today().strftime('%Y%m%d')

    #strings to help compile different file names and paths
    head = "ftp://ftp.nasdaqtrader.com/Files/crosses/CrossStats"
    save_head = 'CrossStats'
    tail = ".txt"
    final_path = file_path + '/individualData'

    #if you set new_lib to true, it will ensure the existing library is empty
    if new_lib == True:
        clear_folder(file_path)
        os.makedirs(final_path)

    dates = dates_between(start, end) #dates between start and end in yyyymmdd

    #initiates the loading bar
    pbar = tqdm(total = len(dates_between(start, end)), position = 0)

    #for each date, try to download raw data, convert it to a csv, and save it
    for num in dates:
        try:
            if (num >= start) and (num <= end):
                raw = download_file_information(head + num + tail)

                file_name = save_head + num + tail
                single_path = final_path + '/' + file_name

                download_csv(raw, single_path)

            pbar.set_description('Processing: ' + file_name)
        except:
            pass
        pbar.update(1)
    pbar.close()

def data_compiler(file_path, period = 'a'):
    """
    [Consumer Use]

    Compiles the data in larger files based on your chosen compilation period

    file_path:
        Description: the path to your main library
        D-type: String
        Notes: Make sure to use '/', not '\' and that this is to your root
               directory for your data, not the 'individualData' file.

    period:
        Description: the period that you choose to compile your data by
        D-type: String
        Notes: 'a': combined by all time (all information in one big file)
               'y': combined by year (one file for each year)
               'm': combined by month (one file for each month)
    """
    #creates paths based on how you want your information grouped
    files = os.listdir(file_path + '/individualData')
    if period == 'a':
        end = 'All'
    elif period == 'm':
        end = 'Month'
        period_files = list(set([i[10:16] for i in files]))
        length = 6
    elif period == 'y':
        end = 'Year'
        period_files = list(set([i[10:14] for i in files]))
        length = 4
    final_path = file_path + '/dataBy' + end
    individual_path = file_path + '/individualData'

    os.makedirs(final_path) #makes correct directory to store the compiled data
    set_path(individual_path) #sets the path that the code is running in

    pbar = tqdm(total = len(files), position = 0) #initiates the loading bar

    #if you are making an all-time data compilation compile ever file
    if period == 'a':
        temp = open('AllData.txt', 'w')
        columns = 'Date,Symbol,ListingMarket,OpeningCross,ClosingCross,' + \
                  'IntradayCross\n'
        temp.write(columns)
        for k in files:
            pbar.set_description('Processing: ' + k)
            pbar.update(1)
            count = 0
            for line in open(file_path + '/individualData/' + k):
                if count != 0:
                    temp.write(line)
                count += 1
        temp.close()
        pbar.close()
        shutil.move(individual_path + '/AllData.txt', \
                    final_path + '/AllData.txt')
    #if you are using one of the other options compile based on that
    else:
        for i in period_files:
            file_name = 'CrossStats' + i + '.txt'
            temp = open(file_name, 'w')
            my_files = [j for j in files if j[10: 10 + length] == i]
            for k in my_files:
                pbar.set_description('Processing: ' + k)
                pbar.update(1)
                for line in open(k):
                    temp.write(line)
            temp.close()
            shutil.move(individual_path + '/' + file_name, \
                        final_path + '/' + file_name)
        pbar.close()

def data_updator(file_path):
    """
    [Consumer Use]
    Downloads new data to keep your library up to date and recompiles it for
    all time, year, or month periods depending if you have one or multiple.

    file_path:
        Description: the path to your main library
        D-type: String
        Notes: Make sure to use '/', not '\' and that this is to your root
               directory for your data, not the 'individualData' file.
    """
    individual_path = file_path + '/individualData' #path to individual data
    final_path = file_path + '/dataByAll' #path to all data group
    set_path(final_path) #sets file path to your directory
    last_date = last_date_downloaded(file_path) #last file downloaded's date

    #if data isnt up to date
    if dt.datetime.today().strftime('%Y%m%d') > last_date:
        #downloads all data after the last date downloaded
        data_downloader(file_path, start = last_date)

        #finds all files downloaded after the last date downloaded
        files = os.listdir(individual_path)
        temp = open('AllData.txt', 'a')
        my_files = [i for i in files if i[10:18] > last_date]

        try:
            pbar = tqdm(total = len(my_files), position = 0) #loading bar init
            #appends new data to all time data file
            for j in my_files:
                temp = open('AllData.txt', 'a')
                for line in open(individual_path + '/' + j):
                    temp.write(line)
                temp.close()
                pbar.set_description('Processing: ' + j)
                pbar.update(1)
            pbar.close()
        except:
            pass
        try:
            #removes dataByMonth directory and recompiles data by month
            os.rmdir(file_path + '/dataByMonth')
            data_compiler(path, period = 'm')
        except:
            pass
        try:
            #removes dataByYear directory and recompiles data by year
            os.rmdir(file_path + '/dataByYear')
            data_compiler(path, period = 'y')
        except:
            pass
