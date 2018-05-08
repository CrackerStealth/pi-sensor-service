[Pi Sensor Service (v0.1)](https://github.com/CrackerStealth/pi-sensor-service)
=================

A simple framework for viewing and receiving data from sensors on a Raspberry Pi.

Application Setup:
------

1. **Install Required Python Libraries**
    
    Connect to your Raspberry Pi as the **pi** user and use the following command to install neccissary Python modules.
    
    ```
    sudo apt-get install python-twisted python-lxml
    ```

2. **Clone Repository**
    
    Clone the contents of the repository to the home directory for the **pi** user on the Raspberry Pi.
    
    ```
    cd ~
    git clone https://github.com/CrackerStealth/pi-sensor-service.git
    ```

3. **Create Config File**
    
    If this the first time install of the software, create a new config file using the sample JSON file.
    
    ```
    cd ~/pi-sensor-service
    cp config.json.sample config.json
    ```
    
    Configure any sensors you want to be accessible through the XML service.

4. **Configure SSL Certificates**
    
    In order for secure communication to be allowed, the controller application needs SSL certificates. By default, the service expects the **certificate** and **key** to be at `/home/pi/pi-sensor-service-cert/localhost.crt` and `/home/pi/pi-sensor-service-cert/localhost.key` respectively. You can either update the locations in the config file or place these items at these locations.
    
    To quickly generate SSL certificates for testing, do the following:
    
    ```
    mkdir -p /home/pi/pi-sensor-service-cert
    openssl req -new -x509 -days 3650 -nodes -out /home/pi/pi-sensor-service-cert/localhost.crt -newkey rsa:4096 -sha256 -keyout /home/pi/pi-sensor-service-cert/localhost.key -subj "/CN=localhost"
    chmod 700 /home/pi/pi-sensor-service
    chmod 600 /home/pi/pi-sensor-service/*
    ```

5. **Configure The Auto-start Service**
    
    This software expects a recent version of Raspian that is using __systemd__.
    
    ```
    sudo cp /home/pi/pi-sensor-service/extra/pisensorserviced.service /lib/systemd/system
    sudo chmod 644 /lib/systemd/system/pisensorserviced.service
    sudo systemctl daemon-reload
    sudo systemctl enable pisensorserviced.service
    sudo systemctl start pisensorserviced.service
    ```

Optional Setup:
-----

1.  **Wi-Fi Auto-Reconnection Script**
    
    Occassionally, when using Wi-Fi, a network connection might get dropped causing access to the garage controller to become unavailable. If you are using the Raspberry Pi built in Wi-Fi interface, you can use the included connection script to re-connect when this happens.
    
    To use the re-connection script, modify the root crontab:
    
    `sudo crontab -e`
    
    Add the following line to check every 5 minutes for a proper connection. Replace **192.168.1.1** with the IP address of your router/gateway or another computer to check against.
    
    `*/5 * * * * sh /home/pi/pi-sensor-service/extra/check-wifi-connection.sh 192.168.1.1 >/dev/null 2>&1`