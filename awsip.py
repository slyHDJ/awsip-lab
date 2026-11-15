import urllib.request
import json
import ipaddress
import sys


def download_aws_ip_set():
  """Downloads the AWS IP range JSON file and returns it as a dictionary."""

  # URL of the AWS IP range JSON file
  aws_ip_range_url = 'https://ip-ranges.amazonaws.com/ip-ranges.json'

  # Download the JSON file
  with urllib.request.urlopen(aws_ip_range_url) as url:
    aws_ip_range_data = json.load(url)

  return aws_ip_range_data['prefixes']


def add_range_details(prefix):
  """Adds details about the IP range."""
  network = ipaddress.ip_network(prefix['ip_prefix'])
  prefix['first_ip'] = str(network[0])
  prefix['last_ip'] = str(network[-1])
  prefix['num_addresses'] = network.num_addresses
  return prefix


# Find ip given IP belongs to any AWS Service
def find_aws_ip(aws_ip_range_data, ip_to_find):
  """Finds the AWS IP range that contains the given IP address."""
  return [add_range_details(prefix) for prefix in aws_ip_range_data
          if ipaddress.ip_address(ip_to_find) in ipaddress.ip_network(prefix['ip_prefix'])]


def smallest_subnet(ips):
  """Returns the smallest subnet that contains all the given IPv4 addresses."""
  addresses = [ipaddress.ip_address(ip) for ip in ips]
  for prefix_length in range(32, -1, -1):
    network = ipaddress.ip_network(f"{addresses[0]}/{prefix_length}", strict=False)
    if all(address in network for address in addresses):
      return network


if __name__ == '__main__':
  if sys.argv[1] == '--subnet':
    # Usage : python awsip.py --subnet 10.0.0.1 10.0.0.7 10.0.0.12
    print(smallest_subnet(sys.argv[2:]))
  else:
    # Usage : python awsip.py 3.5.140.3
    sys.stdout.write(json.dumps(find_aws_ip(download_aws_ip_set(), sys.argv[1]), indent=2))
