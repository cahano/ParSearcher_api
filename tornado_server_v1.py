#####################################################################
### Tornado server, to connect w/ react FE via axios
### 10/4/2023
### Hosted via Heroku
#####################################################################

# Web server
from tornado import gen
from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop
from tornado.options import define, options, parse_command_line
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor

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
from parsing.vanillot_v1 import vanillot_ppm

# init logger
our_log = ParsearchLogger()

# Creating temp directory for file handling
temp_dir = tempfile.TemporaryDirectory(suffix = '.psh')
os.chdir(temp_dir.name)

# Setting port
define("port", default=8008, help="run on the given port", type=int)

MAX_WORKERS = 16

class UploadHandler(RequestHandler):

    def set_default_headers(self):
        '''
        Allows react <-> tornado cnxn
        '''
        # Accepts request originating from OCC github
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



class ParseHandler(RequestHandler):
  executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
  
  def set_default_headers(self):
        '''
        Allows react <-> tornado cnxn
        '''
        # Accepts request originating from OCC github
        self.set_header("Access-Control-Allow-Origin",
                        "https://cahano.github.io")
        
        self.set_header("Access-Control-Allow-Headers",
                        "Origin, X-Requested-With,Content-Type, Accept, Authorization")
        
        self.set_header('Access-Control-Allow-Methods',
                        'GET,HEAD,OPTIONS,POST,PUT,DELETE')
        
        self.set_status(204)



  @gen.coroutine
  def get(self):
    '''
    Initiates the parser, async
    '''
    # Setting input and output file names
    ## TO BE MADE FUNCTIONAL W.R.T. INPUT FILES
    # input_name = 'test_file.pdf'
    output_name = 'parse_results.xlsx'

    our_log.logit('XXX CALLING VANILLOT IN GET')

    # Starting worker for parsing
    yield self.call_vanillot()

    our_log.logit("ZZZZ ENDING CALL KICKING OFF TORNADO")

    self.write('parser initiated')

  @run_on_executor      
  def call_vanillot(self):
    '''
    Runs vanillot parser
    '''
    input_name = 'test_file.pdf'
    output_name = 'parse_results.xlsx'

    our_log.logit('*** CALLING VANILLOT IN COROUTINE')
    our_log.logit('TEMP DIR BEFORE PARSE:')
    our_log.logit(os.listdir())    

    # Calling vanilla PyPDF2 and camelot parser
    vanillot_ppm(input_name,
                 os.getcwd(),
                 output_name)
    
    our_log.logit('TEMP DIR AFTER PARSE:')
    our_log.logit(os.listdir())


class DownloadHandler(RequestHandler):
  
    def set_default_headers(self):
        '''
        Allows react <-> tornado cnxn
        '''
        # Accepts request originating from OCC github
        self.set_header("Access-Control-Allow-Origin",
                        "https://cahano.github.io")
        
        self.set_header("Access-Control-Allow-Headers",
                        "Origin, X-Requested-With,Content-Type, Accept, Authorization")
        
        self.set_header('Access-Control-Allow-Methods',
                        'GET,HEAD,OPTIONS,POST,PUT,DELETE')
        

    @gen.coroutine
    def get(self):
        '''
        Returns outputted parsed file once it has completed
        * This will be pinged by react side until it downloads 
        '''
        our_log.logit('DOWNLOADING PDF(s)')

        output_name = 'parse_results.xlsx'

        # CHecking if parsed results file exists in temp dir
        if output_name in os.listdir():
            # React-side si lookign for this status code to initiate download
            self.set_status(200)
            # Setting headers to deal with xlsx files
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
        else:
            self.set_status(204)
            return




def make_app():
  
    parse_command_line()

    app =  Application([
        ("/upload", UploadHandler),
        ("/parse", ParseHandler),
        ("/download", DownloadHandler),
        ])

    app.listen(options.port)
    IOLoop.instance().start()


if __name__ == '__main__':
    make_app()

