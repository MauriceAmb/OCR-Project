import numpy as np
import pandas as pd
import pytesseract
from pytesseract import Output
from pdf2image import convert_from_path
import re
import os
import ntpath
import mysql.connector


# def pdfToText(fname):
#     pdf = PyPDF2.PdfFileReader(fname)
#     content = ""
#     for page in range(pdf.getNumPages()):
#         content += pdf.getPage(page).extractText()
#     print(content)
#     return content


def pdf_ocr(fname, **args):
    images = convert_from_path(fname, **args)
    text = ''
    for img in images:
        img = np.array(img)
        text += pytesseract.image_to_string(img)

    return text


def pdf_ocr_data(fname, **arg):
    images = convert_from_path(fname, **arg)
    df = pd.DataFrame(
        {
            'level': [],
            'page_num': [],
            'block_num': [],
            'par_num': [],
            'line_num': [],
            'word_num': [],
            'left': [],
            'top': [],
            'width': [],
            'height': [],
            'conf': [],
            'text': []
        }
    )

    for img in images:
        img = np.array(img)
        df = pd.concat([df, pytesseract.image_to_data(img, output_type=Output.DATAFRAME)])
    return df


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def Add_Address_To_CSV(address_db, csv_file):
    address_db.to_csv(path_or_buf=csv_file, index=True, header=True)


def find_adress(fname):

    # To have a clean text
    text = text = pdf_ocr(fname)
    text = text.replace("\n"," ")
    text = text.replace(","," ")
    text = text.replace("-"," ")
    text = text.replace("      ","")
    #df_data = pdf_ocr_data(fname)
        
    # Unused
    height_postal  = 0

    # Dataframe base
    df_db = pd.DataFrame(columns=['Nom de fichier', 'Adresse', 'Code Postal', 'Ville'])

    # First filter
    pattern2 = re.compile(r'((\d{1,5})\s?|-|,| )(\d{1,5}\s|-|,| )?(\d|\s|-|,| )?(AVENUE|RUE|ZAC|PLAINE|QUAI|ALLEE|allée|PASSAGE|PLACE|BOULEVARD|ROUTE|CHEMIN|BOURG|VILLAGE|AV|VAL|CLOS|Hôtel|HOTEL)(\s|-|, )([- a-zA-ZàâäèéêëîïôœùûüÿçÀÂÄÈÉÊËÎÏÔŒÙÛÜŸÇ\d{1,5}\(\)]+)', re.I | re.M)

    matches = re.finditer(pattern2, text)
    #print(matches)

    for match in matches:

        if match is not None:
            # To have localisation. Unused. 
            # df = df_data.loc[df_data['text'] == match.group(2)]

            # To take an adress
            address = match.group()
            address = address.upper()

            # Filters out irrelevant addresses
            pattern3 = re.compile(r'^((?!Tél|Siret|mail|email|Té|Téléphone).)*$', re.I | re.M)
            res3 = pattern3.match(match.group(0))

            # If they are some detected adresses
            if res3 is not None:
                city =""
                postal_code=""
                # Simple postal code filter
                pattern_cp = re.compile(
                    # Simple postal code pattern
                    # r'(.+)(\d{5})(.+)'
                    r'(.+)(\d{2} \d{3}|\d{5}|\(\d{2}\)|\(\d{5}\))(.+)'
                    ,re.I | re.M)
                res_pattern = pattern_cp.match(address)

                # Take adress only if they is a detected postal code
                if res_pattern is not None:
                    postal_code = res_pattern.group(2)
                    # If a potential city is detected after postal code
                    if res_pattern.group(3) is not None:
                        city = res_pattern.group(3)
                    # Simple city cleaning
                    pattern_city_cedex = re.compile(
                        #r'((([a-zA-ZàâäèéêëîïôœùûüÿçÀÂÄÈÉÊËÎÏÔŒÙÛÜŸÇ]+)([-\' ]?[a-zA-ZàâäèéêëîïôœùûüÿçÀÂÄÈÉÊËÎÏÔŒÙÛÜŸÇ]+)?)[ ]?(CEDEX[ ]?([\d]*)))'
                        r'[ ]*(.*)*?(\b[A-ZÀÂÄÈÉÊËÎÏÔŒÙÛÜŸÇ]+[-\' ]?[A-ZÀÂÄÈÉÊËÎÏÔŒÙÛÜŸÇ]*[ ]*?(CEDEX)?[ ]*?[\d]*)(.*)'
                    ,re.I | re.M)
                    res_city_pattern = pattern_city_cedex.match(city)
                    if res_city_pattern is not None:
                        #print("res_city not none !")
                        city = res_city_pattern.group(2)
                    address = res_pattern.group(1)
                    address = address.upper()
                    address = address.strip()

                    # To take adresse height in the document. Unused.
                    #height_postal = df.loc[:, 'height'].max()

                    fnamelight = path_leaf(fname)
                    # To remove the extension filename
                    #fnamelight = os.path.splitext(fnamelight)[0]

                    df_db = pd.concat([df_db,pd.DataFrame([{
                    'Nom de fichier': fnamelight,
                    'Adresse': address,
                    'Code Postal': postal_code,
                    'Ville': city
                    #'Taille caractères':height_postal 
                    }])], ignore_index=True)
                    # Bye index column :
                    df_db.reset_index(drop=True, inplace=True)

                # Take adress only if there is no postal code but a detected city in uppercase
                # Non-functional. Needs comparison with the SQL database.
                # else : 
                #     print("There is no CP")

                    
                    # pattern_city_maj = re.compile(
                    #     r'(.+)(\b[[:upper:]]+\b)(.?)'
                    # ,re.I | re.M)
                    # res_pattern = pattern_city_maj.match(address)

                    # if res_pattern is not None:
                    #     print("There is no CP but an upper word !")
                    #     city = res_pattern.group(2)
                    #     city = city.upper()
                    #     pattern_city_cedex = re.compile(
                    #         r'(([a-zA-ZàâäèéêëîïôœùûüÿçÀÂÄÈÉÊËÎÏÔŒÙÛÜŸÇ]+)([-\' ]?[a-zA-ZàâäèéêëîïôœùûüÿçÀÂÄÈÉÊËÎÏÔŒÙÛÜŸÇ]+)?)[ ]?((CEDEX)[ ]?([\d]*))'
                    #         ,re.I | re.M)
                    #     res_city_pattern = pattern_city_cedex.match(city)
                    #     if res_city_pattern is not None:
                    #         city = res_city_pattern.group(2)
                    #     if res_pattern.group(1) is not None :
                    #         address = res_pattern.group(1)
                    #     else :
                    #         address = res_pattern.group(3)
                    #     address = address.upper()
                    #     height_postal = df.loc[:, 'height'].max()
                    #     fnamelight = path_leaf(fname)
                    #     fnamelight = os.path.splitext(fnamelight)[0]

                        # df_db = pd.concat([df_db,pd.DataFrame([{
                        #     'Nom de fichier': fnamelight,
                        #     'Adresse': address,
                        #     'Code Postal': postal_code,
                        #     'Ville': city,
                        #     'Taille caractères': height_postal 
                        # }])], ignore_index=True)
                        # # Bye index column :
                        # df_db.reset_index(drop=True, inplace=True)

    # Empty dataframe exception
    if df_db.empty:
        raise Exception("no address detected")
    
    return df_db
  
def occurence(df, colName):
    #print("Is there one or more ?")
    df = pd.DataFrame(df)
    occurrences = df['Adresse'].value_counts()
    df['Nombre Occurrence'] = df['Adresse'].apply(lambda x: occurrences[x])

    df.reset_index(drop=True, inplace=True)
    
     # Extraction of the addresses column
    addresses = df[colName]

    # Creation of a dictionary to store the number of duplicates for each address
    address_dict = {}

    # Comparison of each address with all the other addresses
    for i in range(len(addresses)):
        for j in range(i + 1, len(addresses)):
            if i != j:
                if addresses[i] == addresses[j]:
                    address = addresses[i]
                    if address not in address_dict:
                        address_dict[address] = 1
                    else:
                        address_dict[address] += 1

    # Creation of a dataframe containing the addresses and the number of duplicates for each address
    result = pd.DataFrame({
        'Adresse': list(address_dict.keys()),
        #'Nombre Occur': list(address_dict.values())
    })
    # result.reset_index(drop=True, inplace=True)
    result = pd.merge(df, result, on='Adresse', how='left')

    return result


def csv_write(df):
    # CSV file writingmatches
    with open('adressList.csv','a') as csv_file:
        Add_Address_To_CSV(df, csv_file)
        # Bye index column :
        df.reset_index(drop=True, inplace=True)  
    print(df)
    
    return df



def compare_city_name(df):
    # Connect to the database
    connection = mysql.connector.connect(
        host="",
        user="root",
        password="mynewpassword",
        database="villes_tests"
    )
    cursor = connection.cursor()

    # Split the string into words
    df = df.astype(str)
    words = df.apply(lambda x: x.split())  

    # Iterate over each word and compare it with the city_name
    for word in words:
        word = word.astype(str)
        query = f"SELECT ville_nom FROM villes_france_free WHERE ville_nom = '{word}'"
        cursor.execute(query)

        result = cursor.fetchone()
        if result is not None:
            return result

    # Close the cursor and the connection
    cursor.close()
    connection.close()

    return "No city match"

def getCityName(df):
    # Connect to the database
    connection = mysql.connector.connect(
        host="",
        user="root",
        password="mynewpassword",
        database="villes_tests"
    )
    cursor = connection.cursor()

    # Iterate over each row of the dataframe
    for index, row in df.iterrows():
        # Get the postal code from the row
        cp = row['Code Postal']
        cp = cp.replace(" ", "")


        # Execute the SQL query to get the city names for the postal code
        query = f"SELECT ville_nom FROM villes_france_free WHERE ville_code_postal = '{cp}'"
        cursor.execute(query)

        # Fetch all the results and concatenate them into a single string
        results = cursor.fetchall()
        if results:
            cities = [result[0] for result in results]
            city_str = ', '.join(cities)
            df.at[index, 'Ville'] = city_str

    # Close the cursor and the connection
    cursor.close()
    connection.close()

    return df


def get_zip_code(df, colName):
    conn = mysql.connector.connect(
        host="",
        user="root",
        password="mynewpassword",
        database="villes_tests"
    )
    cursor = conn.cursor()
    query = "SELECT ville_code_postal FROM villes_france_free WHERE ville_code_postal = %s"
    #cursor.execute(query, (city,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return "(No ZIP CODE)"
    
def is_pdf(file):
    fnamelight = path_leaf(file)
    extension = os.path.splitext(fnamelight)[1]
    #print(extension)
    if (extension=='.pdf')|(extension=='.PDF'):
        return True
    else:
        return False

def addresses_for_one_document(file):
    # find all adresses of the document in a dataframe
    address_db = find_adress(file)
    # Modify adresses occurence
    df_complet = occurence(address_db,'Adresse')

    # Add correct city name with detected postal code
    #df_complet = getCityName(df_complet)

    # Write the dataframe
    csv_write(df_complet)


def all_adresses_for_all_documents(directory):
    dir_list = os.listdir(directory)
    #print(dir_list)
    # iterate over files in this directory
    for filename in dir_list:
        f = os.path.join(directory, filename)
        # check if it is a pdf file
        if os.path.isfile(f) and is_pdf(f):
            #print(filename)
            #print(is_pdf(filename))
            addresses_for_one_document(f)
    

if __name__ == '__main__':

    # Folder path
    #directory = r'/home/cytech/Desktop/ING3/PFE/Rapports/++'
    #all_adresses_for_all_documents(directory)

    # file test path
    file =  r'./Rapports/11.pdf'
    addresses_for_one_document(file)

    #ville  = compare_city_name(address_db['Adresse'])
    #print(ville,zip)