import datetime
import json
import socket
import syslog

from lxml import etree
from twisted.internet import reactor
from twisted.internet import ssl
from twisted.internet.protocol import Protocol
from twisted.web import server
from twisted.web.resource import Resource
from twisted.web.static import File

from temperature import *
from errors import *

TYPE_TEMPERATURE = 'temperature'        # Keyword for a temperature sensor from JSON config file.
TEMPLATE_LIST = 'template/list.html'    # Relative path to the template for the list sensors HTML page.

# This resource handler is used to generate the list.html page
# which provides a table of all active sensors
class ListHandler(Resource):
    isLeaf = True
    obj_list = None
    
    def __init__ (self, sensor_obj):
        Resource.__init__(self)
        self.obj_list = sensor_obj

    def render(self, request):
        # Load the XML of the template file
        list_page = etree.parse(TEMPLATE_LIST)
        
        # Add the host name to the <p> element with id 'hoststring'
        hostname_element = list_page.find('.//span[@id="hoststring"]')
        hostname_element.text = socket.gethostname()
        
        # Add the current date to the <p> element with id 'datestring'
        date_element = list_page.find('.//span[@id="datestring"]')
        date_element.text = str(datetime.datetime.now())
        
        # Find the table with the id 'sensortabe' and add rows from all the sensors
        list_table_element = list_page.find('.//table[@id="sensortable"]')
        for o in self.obj_list:
            list_table_element.append(o.getHTML())
            
        # Return rendered HTML to the client
        return etree.tostring(list_page, pretty_print=True)

# This resource handler is used to provide XML output for the sensor.xml
# resource request. A GET request parameter 'sensor' can get added with
# the name of the sensor being queries. Otherwise, returns all sensors.
class ServiceHandler(Resource):
    isLeaf = True
    obj_list = None
    
    def __init__ (self, sensor_obj):
        Resource.__init__(self)
        self.obj_list = sensor_obj

    def render(self, request):
        # We are returning XML to the client
        request.setHeader('Content-Type', 'application/xml')
        
        # Create the root element of the response
        root_item = etree.Element('service')
        
        # Add a hostname element to the response
        hostname_element = etree.Element('hostname')
        hostname_element.text = socket.gethostname()
        root_item.append(hostname_element)
        
        # Add a date element to the response
        date_element = etree.Element('date')
        date_element.text = str(datetime.datetime.now())
        root_item.append(date_element)
        
        # Create the sensors element
        sensors_element = etree.Element('sensors')
        
        # Try and read the GET parameter 'sensor'. If it fails, parameter was not supplied.
        try:
            # Looking for a sensor by its name
            sensor_name = request.args['sensor'][0]
            for o in self.obj_list:
                if o.name == sensor_name:
                    sensors_element.append(o.getXML())
        # Could not read 'sensor' parameter, return all.
        except:
            # Loop through all the sensors to add to the response.
            for o in self.obj_list:
                sensors_element.append(o.getXML())     
        
        # Add the ensors to the response.
        root_item.append(sensors_element)
        
        # Return XML in string form to the client.
        return etree.tostring(root_item, pretty_print=True, xml_declaration=True, encoding='UTF-8')


if __name__ == '__main__':
    # List of sensor objects
    sensor_obj = []
    
    # Enable logging for the application
    syslog.openlog('pi_sensor_service')
    
    # Read from the config file
    config_file = open('config.json')
    config = json.load(config_file)
    config_file.close()
    
    # Read the standard config items
    listen_port = config['listen_port']
    ssl_key = config['ssl_key']
    ssl_cert = config['ssl_cert']
    
    # Read the sensor types from the JSON file
    for (n,c) in config['sensors'].items():
        name = n
        sensor = c['sensor']
        type = c['type']
        location = c['location']
        unit = c['unit']
        enabled = c['enabled']
        if sensor == TYPE_TEMPERATURE:
            sensor_obj.append(Temperature(type, location, unit, name))
        else:
            raise ConfigError('Unknown sensor type: ' + type)

    # Create the SITE to be hosted by our service
    root = File('www')
    root.putChild('sensor.xml', ServiceHandler(sensor_obj))
    root.putChild('list.html', ListHandler(sensor_obj))
    site = server.Site(root)
    
    # Start the HTTPS server for the service
    sslContext = ssl.DefaultOpenSSLContextFactory(ssl_key, ssl_cert)
    reactor.listenSSL(listen_port, site, sslContext)
    reactor.run()
