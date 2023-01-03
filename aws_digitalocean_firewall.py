import requests
import json
import os


class DigitalOcean:
    """ This class gets, updates and puts Digital Ocean firewalls through their API.

        Parameters:
        api_token (str):  API token generated in Digital Ocean.
        firewall_id (str):  Firewall id of the firewall you want to manipulate.
    """
    def __init__(self, api_token, firewall_id):
        self.api_token = api_token
        self.firewall_id = firewall_id

    def get_rules(self):
        """ Gets the firewall rules by firewall id

        Parameters:

        Returns:
        dict:Returning Returns the rules of the firewall
        """
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_token}',
        }
        try:
            response = requests.get(f'https://api.digitalocean.com/v2/firewalls/{self.firewall_id}', headers=headers)
            if response.status_code == 200:
                self.rules_json = response.json()
                print("Current rules...")
                print(self.rules_json)
                return self.rules_json
            else:
                print(response.text)
                raise SystemExit(f"GET Failure with Digital Ocean: Status {response.status_code}")
        except Exception as e:
            print(e)

    def put_rules(self):
        """ Puts updated rules back to the firewall

        Parameters:

        Returns:
        str:Returning Returns the response from Digital Ocean.
        """
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_token}',
        }
        try:
            response = requests.put(f'https://api.digitalocean.com/v2/firewalls/{self.firewall_id}', headers=headers, json=self.rules_json["firewall"])
            if response.status_code == 200:
                print("Sending...")
                print(self.rules_json["firewall"])
                print("Response...")
                print(response.text)
                return response.text
            else:
                print(response.text)
                raise SystemExit(f"PUT Failure with Digital Ocean: Status {response.status_code}")
        except Exception as e:
            print(e)

    def update_rules(self, inbound_rules, ports):
        """ Updates the rules variable self.rules_json which was retrieved by the get_rules method.

        Parameters:
        inbound_rules (list):  A list of IP ranges to be added to the firewall.
        ports (list): A list of ports to to be added to each of the inbound rules.

        Returns:
        """
        port_exists = False
        self.inbound_rules = inbound_rules
        self.ports = ports
        # print(self.rules_json["firewall"]["inbound_rules"])
        del self.rules_json["firewall"]["id"]
        del self.rules_json["firewall"]["status"]
        del self.rules_json["firewall"]["created_at"]
        del self.rules_json["firewall"]["pending_changes"]
        for port in ports:
            for firewall_rule in self.rules_json["firewall"]["inbound_rules"]:
                if firewall_rule["ports"] == port:
                    firewall_rule["sources"]["addresses"] = inbound_rules
                    # print(firewall_rule["sources"]["addresses"])
                    port_exists = True
            if port_exists is False:
                self.rules_json["firewall"]["inbound_rules"].append({
                    "protocol": "tcp",
                    "ports": port,
                    "sources": {
                        "addresses": inbound_rules
                    }
                })
        # print(self.rules_json["firewall"]["inbound_rules"])
        return

    @staticmethod
    def pretty_print_json(request_response):
        """ Pretty Prints JSON

        Parameters:
        request_response (dict):  Dict to be pretty printed in JSON format.

        Returns:
        """
        resp_dict = request_response
        pretty = json.dumps(resp_dict, indent=2)
        print(pretty)
        return


class Aws:
    """ This class gets, updates and puts Digital Ocean firewalls through their API.

        Parameters:
        service (str):  Specify the service you want to pull AMAZON ip address from.
        ip_ranges_url (str):  The URL of the ip ranges from AWS.
    """

    def __init__(self, service, ip_ranges_url):
        self.service = service
        self.ip_ranges_url = ip_ranges_url

    def get_ipranges(self):
        """ Gets ip ranges from AWS IP ranges URL

        Parameters:

        Returns:
        list:Returning Returns filter list of ip address ranges by aws service.
        """
        headers = {
            'Content-Type': 'application/json'
        }
        try:
            response = requests.get('https://ip-ranges.amazonaws.com/ip-ranges.json', headers=headers)
            if response.status_code == 200:
                response = requests.get(ip_ranges_url, headers=headers)
                ip_ranges_json = response.json()
                ip_ranges = ip_ranges_json["prefixes"]
                ip_ranges_filtered = []
                # DigitalOcean.pretty_print_json(ip_ranges)
                for ip_range in ip_ranges:
                    if ip_range["service"] == service:
                        # print(ip_range)
                        ip_ranges_filtered.append(ip_range["ip_prefix"])
                return ip_ranges_filtered
            else:
                print(response.text)
                raise SystemExit(f"GET Failure with AWS: Status {response.status_code}")
        except Exception as e:
            print(e)


api_token = os.environ['DIGITALOCEAN_TOKEN']
firewall_id = os.environ['DIGITALOCEAN_FIREWALL_ID']
service = "CLOUDFRONT"
ip_ranges_url = "https://ip-ranges.amazonaws.com/ip-ranges.json"

firewall = DigitalOcean(api_token, firewall_id)
firewall_rules = firewall.get_rules()
# DigitalOcean.pretty_print_json(firewall_rules)
aws_cloudfront_ips = Aws(service, ip_ranges_url)
inbound_rules = aws_cloudfront_ips.get_ipranges()
firewall.update_rules(inbound_rules, ["443", "80"])
firewall.put_rules()
