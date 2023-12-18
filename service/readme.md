## How to use:

1) Copy `tacitus-api.service` into `/etc/systemd/system/`
    - `sudo cp tacitus-api.service /etc/systemd/system/`
0) Customise `tacitus-api.service` to your needs.
    - `sudo vim /etc/systemd/system/tacitus-api.service`
0) Reload systemd daemon.
    - `sudo systemctl daemon-reload`
0) Start the service.
    - `sudo systemctl start tacitus-api.service`
0) Check the status of the service.
    - `sudo systemctl status tacitus-api.service`
0) Enable the service to start on boot.
    - `sudo systemctl enable tacitus-api.service`
0) Check enpoint is working.
    - `curl http://<Your server address>:8155/`