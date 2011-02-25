import os
import sys
import traceback
import arcgisscripting


DEBUG = True

# Create the geoprocessing object
# in the global scope so it's available
# to all script functions
gp = arcgisscripting.create()

class SvmpError(Exception): pass

def pretty(msg):
  """Pretty print an error message in an ascii box.
  """
  global gp
  if isinstance(msg,Exception):
   msg_len = len(msg.message)
  else:
   msg_len = len(msg)
  wrap = '\n|%s--|' % (msg_len*'-')
  wrap += '\n| %s |\n' % msg
  wrap += '|%s--|\n' % (msg_len*'-')
  return wrap


def err(msg=None):
  """ Custom error output for Geoprocessing scripts.
  
  Returns formatting error message, GP errors (if they exist)
  and python tracebacks if DEBUG=True.
  
  TODO: generate more or less verbose output based on exception type.
  
  http://webhelp.esri.com/arcgisdesktop/9.2/index.cfm?TopicName=GetMessages_method
  """
  global gp
  tb = sys.exc_info()[2]
  tbinfo = traceback.format_tb(tb)[0]
  py_error = 'Python Error:\nTraceback:\n%s\nInfo:\n\t%s: %s\n' % (tbinfo,sys.exc_type,sys.exc_value)
  arc_error = 'Geoprocessing Error:\n%s\n' % gp.GetMessages(2)
  #x = 0
  #while x < gp.MessageCount:
  #  gp.AddReturnMessage(x)
  #  x = x + 1
  if gp.GetMessages(2):
    gp.AddError(pretty(msg))
    gp.AddError(arc_error)
    if DEBUG:
      gp.AddError(py_error)
  else:
    gp.AddError(pretty(msg))
    if DEBUG:
      gp.AddError(py_error)
  #raise SVMPException('fatal SVMP error')
  del gp
  #raise

def main():
  global gp
  gp.AddMessage('Adding a test message...')
  
  #raise SvmpError('Custom python exception error here...')
  
  try:
    raise RuntimeError
  except Exception, E:
    err('An intentional RuntimeError occurred in the python script..')
  

if __name__ == "__main__":
  try:
    main()
  except Exception, E:
    err(E)

