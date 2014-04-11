import subprocess

from lxml import etree

from errors import *

TYPE_DS18B20 = 1                        # Numeric value for the 1-Wire DS18B20 temperature sensor
TYPE_DS18B20_DESC = 'DS18B20'           # String description for the 1-Wire DS18B20 temperature sensor
UNIT_CELSIUS = 'C'                      # Unit to represent Celsius temperature
UNIT_FAHRENHEIT = 'F'                   # Unit to represent Fahrenheit temperature
UNIT_KELVIN = 'K'                       # Unit to represent Kelvin temperature
DEVICES_DIR = '/sys/bus/w1/devices/'    # File path to the 1-Wire devices

# This class is used for interacting with the DS18B20 1 wire temperature sensor
class TempDS18B20 ():
    sensor_location = None
    sensor_type = TYPE_DS18B20
    
    # Initialize the modules at the OS level to interact with the temperature sensor.
    def __init__ (self, location):
        subprocess.call(['modprobe', 'w1-gpio'])
        subprocess.call(['modprobe', 'w1-therm'])
        self.sensor_location = DEVICES_DIR + location + '/w1_slave'

    # We read the temperature from the actual device itself in the file/folder structure.
    def readValue(self):
        sensor_file = open(self.sensor_location)
        sensor_reader = sensor_file.read()
        sensor_file.close()
        
        sensor_line = sensor_reader.split('\n')[1]
        sensor_data = sensor_line.split(' ')[9]
        
        sensor_value =  float(sensor_data[2:])
        sensor_value = sensor_value / 1000
        return sensor_value
    
    # Return numeric temperature sensor type value.
    def getType(self):
        return TYPE_DS18B20

    # Return descriptive temperature sensor type.
    def getTypeDesc(Self):
        return TYPE_DS18B20_DESC
    
    # Return the units being used.
    def getUnit(Self):
        return UNIT_CELSIUS

# Generic class to handle all types of temperature sensors.
class Temperature():
    name = None
    unit = None
    temp_sensor = None

    # Create an instance of a sensor type based on our initialized parameters
    def __init__ (self, type, location, unit, name):
        self.name = name
        self.unit = unit
        if type == TYPE_DS18B20:
            self.temp_sensor = TempDS18B20(location)
        else:
            raise ConfigError('Invalid temperature sensor type.')

    # Return current sensor value
    def getValue(self):
        return self.temp_sensor.readValue()

    # Return the XML formatted version of sensor output.
    def getXML(self):
        element = etree.Element('temperature')
        
        element.set('name', self.name)
        element.set('type', str(self.temp_sensor.getType()))
        element.set('type_desc', self.temp_sensor.getTypeDesc())
        element.set('unit', self.temp_sensor.getUnit())
        
        element.text = repr(self.temp_sensor.readValue())
        
        return element

    # Return the HTML formatted version of the sensor output. Table row view to be used in an HTML page with a <table> element.
    def getHTML(self):
        root = etree.Element('tr')
        
        # Add the 'sensor class' HTML column
        element = etree.Element('td')
        element.text = 'Temperature'
        root.append(element)
        
        # Add the 'sensor name' HTML column
        element = etree.Element('td')
        element.text = self.name
        root.append(element)
        
        # Add the 'numeric sensor type' HTML column
        element = etree.Element('td')
        element.text = str(self.temp_sensor.getType())
        root.append(element)
        
        # Add the 'descriptive sensor type' HTML column
        element = etree.Element('td')
        element.text = self.temp_sensor.getTypeDesc()
        root.append(element)

        # Add the 'sensor value' HTML column
        element = etree.Element('td')
        element.text = repr(self.temp_sensor.readValue())
        root.append(element)
        
        # Add the 'sensor output units' HTML column
        element = etree.Element('td')
        element.text = self.temp_sensor.getUnit()
        root.append(element)
        
        return root
