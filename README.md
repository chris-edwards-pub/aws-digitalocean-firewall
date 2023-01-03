# AWS to Digital Ocean Firewall by API

This is a quick and dirty script that takes the AWS Cloudfront IP addresses from the AWS IP ranges URL and then updates
a DigitalOcean firewall through their API.   I wanted to restrict access to a dropplet to only be accessible from 
AWS Cloudfront IP address. 

I am not sure if anyone will ever use this code but I figured I would throw it out there.



## Install

```console
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt 
```

## Set Enviroment Variables

```bash
export DIGITALOCEAN_TOKEN=
export DIGITALOCEAN_FIREWALL_ID=
```