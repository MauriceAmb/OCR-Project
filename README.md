# OCR PROJECT
***
This Python code allows you to extract postal addresses from PDF reports. It includes several functions that use the Pytesseract OCR engine and the Pdf2image library. The extracted addresses are stored in a Pandas DataFrame that can be exported to a CSV file.

## FUNCTIONS
***
`pdf_ocr(fname, **args)`:
This function takes a PDF file path as input and returns a string containing the extracted text. It uses the Pytesseract OCR engine and the Pdf2image library to convert the PDF pages to images and then extract the text from the images.

`pdf_ocr_data(fname, **arg)`:
This function takes a PDF file path as input and returns a Pandas DataFrame containing the OCR output in a structured format. It uses the Pytesseract OCR engine and the Pdf2image library to convert the PDF pages to images and then extract the text, block, paragraph, line and word coordinates along with the confidence level for each recognized character.

`path_leaf(path)`:
This function takes a file path as input and returns the filename of the file without the path.

`Add_Address_To_CSV(address_db, csv_file)`:
This function takes a Pandas DataFrame containing the extracted addresses and a CSV file path as input and writes the DataFrame to the CSV file.

`find_adress(fname)`:
This function takes a PDF file path as input and returns a Pandas DataFrame containing the extracted postal addresses. It uses the pdf_ocr function to extract the text from the PDF file and then applies regular expressions to identify and extract the addresses. The extracted addresses are then stored in a Pandas DataFrame along with the filename of the PDF report.

`occurence(df, colName)`:
This function takes a dataframe `df` and a column name `colName` as input. It extracts the column of addresses, creates a dictionary to store the number of duplicates for each address, compares each address with all the other addresses, and creates a dataframe containing the addresses and the number of duplicates for each address. It returns the resulting dataframe.

`csv_write(df)`:
This function takes a dataframe `df` as input and writes it to a CSV file named "adressList.csv". It then removes the index column from the dataframe and returns it.

`compare_city_name(df)`:
This function takes a dataframe `df` as input and compares each word in the dataframe with the `ville_nom` column in the `villes_france_free` table of a MySQL database. If a match is found, the function returns the matching city name. Otherwise, it returns "No city match".

`getCityName(df)`:
This function takes a dataframe `df` as input and iterates over each row of the dataframe. It extracts the postal code from each row, executes an SQL query to get the city names for the postal code from the villes_france_free table of a MySQL database, and concatenates the results into a single string. It then adds the city name(s) to the dataframe and returns it.

`get_zip_code(df, colName)`:
This function takes a dataframe `df` and a column name `colName` as input. It connects to a MySQL database, executes an SQL query to get the `ville_code_postal` column from the `villes_france_free` table for the specified postal code, and returns the result.

`is_pdf(file)`:
This function takes a file path file as input and returns True if the file extension is ".pdf" or ".PDF", and False otherwise.

`addresses_for_one_document(file)`:
This function takes a file path file as input, finds all the addresses in the document, modifies their occurrence, adds the correct city name with the detected postal code, and writes the resulting dataframe to a CSV file named "adressList.csv".

`all_adresses_for_all_documents(directory)`:
This function takes a directory path as input, finds all PDF files in that directory, and then calls another function named `addresses_for_one_document` with the PDF file path as an input parameter to get the addresses for each document.

# SQL DATABASE
***
The program uses a MySQL database to compare the postal codes extracted from the PDF files with a list of French cities and their corresponding postal codes. The database can be created by running the SQL script `villes_france_free.sql`. This script contains all the queries necessary to create the `villes_france_free` table used by the program.

## Usage
***
To use the program, follow these steps:

1. Install the necessary Python libraries listed in the Dependencies section of the readme.
2. Create a MySQL database with `villes_france_free.sql` file to create the villes_france_free table.
3. Run the addresses_for_one_document function with the path to the PDF file as input.
4. The resulting CSV file named "adressList.csv" will contain the detected addresses.

You can also use `find_adress` function with the path to the PDF file as input. The extracted addresses will be returned as a Pandas DataFrame. 
Then the Add_Address_To_CSV function to write the addresses to a CSV file if required.

The program is not 100% functional nor 100% complete, but it can extract potential main addresses from PDF reports.

The program allows you to extract addresses from multiple documents using the `all_adresses_for_all_documents` function. The only thing to change is the directory variable to change the folder.


## Dependencies
***
The code requires the following Python libraries to be installed:

    numpy
    pandas
    pytesseract
    pdf2image
    re
    os
    ntpath
    mysql.connector

## Note
***
This code has been developed and tested on a Linux environment. It may require modifications to run on a Windows or Mac environment.
Errors can occur if no address is detected in a document.