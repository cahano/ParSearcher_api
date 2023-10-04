#####################################################################
### Testing pulling pdf data as text, mining for tagging data
### 9/25/2023
### PyPDF2, pdfminer
#####################################################################


import os

# PDF text extractor
from PyPDF2 import PdfReader


class ParsePDF:

    def __init__(self, pdf_path):
        '''
        Path to desired PDF file
        '''
        self.input_file = pdf_path
        

    def PyPDF2_parse(self):
        '''
        Extracts PDF high-level info and contents using PyPDF2 lib

        :returns: PDF contents as str, or None
        '''

        self.pdf_contents = ''
        with open(self.input_file, 'rb') as f:

            # PyPDF2 object
            py_pdf = PdfReader(f)

            # High-level PDF info
            self.info = py_pdf.metadata
            self.number_of_pages = len(py_pdf.pages)

            self.pdf_contents = ''
            # Extracting PDF contents
            for i in range(0, self.number_of_pages):
                page = py_pdf.pages[i]
                self.pdf_contents += page.extract_text()

        return self.pdf_contents \
               if len(self.pdf_contents) > 0 \
               else None 
    

    ### ADD funcs for pdfminer extractor, PyMu, additional java-based pdf parser libs
    def pdfminer_parse(self):
        '''
        '''
        return None

# #### TESTING

# import timeit

# # Setting wd to get pdf
# os.chdir(r'C:\Users\owen_\Desktop\CareerRel\O1\py_related\full_stack\ParseDF\test_docs')



# x = ParsePDF('JPMMT_2007_ppm.pdf')

# # Starting timer
# start_time = timeit.default_timer()


# contents = x.PyPDF2_parse()

# print(contents)

# with open('ppm_output.txt', "w", encoding="utf-8") as txt_file:
#     txt_file.write(contents)

# # print(contents)




# # Ending timer
# end_time = timeit.default_timer()

# print()
# print('~~~~~~~~~ runtime: %f ~~~~~~~~~' % (end_time - start_time))
