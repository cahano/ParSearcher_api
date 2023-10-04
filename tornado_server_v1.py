#####################################################################
### Tornado server, to connect w/ react FE via axios
### 10/4/2023
### Hosted via Heroku
#####################################################################

# Web server
from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop
from tornado.options import define, options, parse_command_line

# Libs for handling file upload, processing, and user download
import tempfile
import os
import sys

# Needed to add this to ensure logger imported succesfully
## something with my file structure
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

# Logger
from our_logger.parsearch_logger import ParsearchLogger

# Parsing lib
from parsing.camelot_parser_v1 import camelot_to_xlsx

# init logger
our_log = ParsearchLogger()

# Creating temp directory for file handling
temp_dir = tempfile.TemporaryDirectory(suffix = '.psh')
os.chdir(temp_dir.name)

# Setting port
define("port", default=8008, help="run on the given port", type=int)


class UploadHandler(RequestHandler):

    def set_default_headers(self):
        '''
        Allows react <-> tornado cnxn
        '''
        self.set_header("Access-Control-Allow-Origin",
                        "https://cahano.github.io")
        
        self.set_header("Access-Control-Allow-Headers",
                        "Origin, X-Requested-With, Content-Type, Accept, Authorization")
        
        self.set_header('Access-Control-Allow-Methods',
                        'GET,HEAD,OPTIONS,POST,PUT,DELETE')
        
        self.set_status(204)

    def post(self):
        '''
        Retrieving pdf bytes from FE
        '''
        our_log.logit('Uploading PDF(s)')

        # Matching tornado structure 
        pdf_bytes = self.request.files['file'][0]['body']
        
        our_log.logit('PDF(s) Uploaded')

        # Writing uploaded pdf bytes to temp directory
        with open('test_file.pdf', 'wb') as f:
            f.write(pdf_bytes)



class DownloadHandler(RequestHandler):
  
  def set_default_headers(self):
        '''
        Allows react <-> tornado cnxn
        '''
        self.set_header("Access-Control-Allow-Origin",
                        "https://cahano.github.io")
        
        self.set_header("Access-Control-Allow-Headers",
                        "Origin, X-Requested-With,Content-Type, Accept, Authorization")
        
        self.set_header('Access-Control-Allow-Methods',
                        'GET,HEAD,OPTIONS,POST,PUT,DELETE')
        
        self.set_status(204)

  def get(self):
    '''
    Parsing pdf doc and returning xlsx ouput
    '''
    # Setting input and output file names
    ## TO BE MADE FUNCTIONAL W.R.T. INPUT FILES
    input_name = 'test_file.pdf'
    output_name = 'parse_results.xlsx'

    our_log.logit('Parsing PDF(s)')

    our_log.logit('TEMP DIR BEFORE PARSE:')
    our_log.logit(os.listdir())

    # Calling camelot PDF parser -> xlsx output
    ## HARD CODED PAGES FOR NOW (FOCUSING ON GLOSSARY OF TERMS)
    ### LOGIC TO BE ADDED THAT WILL DETECT GLOSSARY OF TERMS, ANNEX A, etc
    #### SUCH THAT NO PAGE NUMBER WILL BE PASSED IN
    ##### RATHER PDF(S) AND A DICT W LOGIC DESCRIBING WHAT DATA TO GET FROM THOSE PDF(S)
    camelot_to_xlsx(os.getcwd(),
                    input_name,
                    os.getcwd(),
                    output_name,
                    '79-93')

    our_log.logit('PDF(s) Parsed')

    our_log.logit('TEMP DIR AFTER PARSE:')
    our_log.logit(os.listdir())
    our_log.logit(os.getcwd())

    # Setting headers to deal with xml files
    self.set_header('Content-Type',
                    'application/vnd.openxmlformats-officedocument.spreedsheetml.sheet')
    self.set_header('Content-Disposition',
                    'attachment; filename=%s' % output_name)
    # Handling results XLSX file download
    with open(output_name, 'rb') as pdf:
        while True:
            _buf = pdf.read(4096)
            if _buf:
                self.write(_buf)
            else:
                pdf.close()
                self.finish()
                return
            

def make_app():
  
    parse_command_line()

    app =  Application([
        ("/upload", UploadHandler),
        ("/download", DownloadHandler)
        ])

    app.listen(options.port)
    IOLoop.instance().start()


if __name__ == '__main__':
    make_app()

