# Economic-Analysis
A package that I created for scraping and combining the many individual files of stock data into a more usable format for analytics and updating that data when necessary.

There are many functions in this package that can be used and documentation can be found for everything in the program file, but the only functions necessary for consumer use are documented below.

## Documentation
#### nasdaqtraderscraper.data_downloader(file_path, start = '20080101', end = None, new_lib = False):

    This is a tool used to add to a data library or create a new one and fill it with the pieces of individual 
    data from NASDAQtrader.com.

    file_path:
        Description: the path to your main library (the root directory that you have created)
        D-type: String
        Notes: Make sure to use '/', not '\' and that this is to your root
               directory for your data, not the 'individualData' file.

    start:
        Description: the beginning date for data you want to download (inclusive)
        D-type: String
        Notes: yyyymmdd format
               if this is not specified it defaults to the beginning of the data the website offers
        
    end:
        Description: the ending date for data you want to download (inclusive)
        D-type: String
        Notes: yyyymmdd format
               if this is not specified it sets itself to the current date

    new_lib:
        Description: whether or not you want your library to start from scratch
        D-type: Boolean
        Notes: (WARNING) if True, delets all files and folders in the given directory
        
#### nasdaqtraderscraper.data_compiler(file_path, period = 'a'):

    Compiles the data in larger files based on your chosen compilation period
    [SHOULD ONLY BE USED RIGHT AFTER CREATING A NEW DIRECTORY]
    Other than that, the data_updator method will recompile everything for you

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
        
#### nasdaqtraderscraper.data_updator(file_path):

    Downloads new data to keep your library up to date and recompiles it for
    all time, year, or month periods depending if you have one or multiple.

    file_path:
        Description: the path to your main library
        D-type: String
        Notes: Make sure to use '/', not '\' and that this is to your root
               directory for your data, not the 'individualData' file.
