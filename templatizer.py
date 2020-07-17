import conf, ipaddress
from jinja2 import FileSystemLoader, Environment


class Templater:
    def __init__(self):
        self.alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVQWXYZ'
        self.ticket_number = input('Enter a ticket number: ')
        self.client_code = input('Enter a client code: ').upper()
        self.tier_two_asa = ''
        self.object_group_tier2 = ''
        self.object_group_tier1 = ''
        self.hosts = []
        self.out_file = f"{conf.output_dir}/{self.ticket_number}.txt"
        self.in_file = f"{conf.input_dir}/{self.ticket_number}.txt"
        self.jinjenv = Environment(
            loader=FileSystemLoader(conf.templates_dir)
        )
        self.build_hosts()

    def add_hosts(self, host):
        try:
            ipaddress.ip_address(host.replace('\n', ''))
            self.hosts.append(f"host {host}")
        except Exception as e:
            print(e)
            self.hosts.append(f"fqdn {host}")

    def build_hosts(self):
        try:
            with open(self.in_file) as hosts_file:
                for host in hosts_file:
                    self.add_hosts(host)
        except FileNotFoundError as e:
            print('No matching input file. Please create a file to match the ticket number (eg, NET-123.txt)')
            print(e)
            print('Exiting Script . . .')

    def render_ganalytics_template(self):
        ganalytics_template = self.jinjenv.get_template('ganalytics')
        return_template = ganalytics_template.render(
            ticket_number=self.ticket_number,
            client_code=self.client_code,
            ip_addresses=self.hosts

        )
        return return_template

    def render_tools_pd_template(self):
        tools_pd_template = self.jinjenv.get_template('pd-tools')
        return_template = tools_pd_template.render(
            ticket_number=self.ticket_number,
            client_code=self.client_code,
            ip_addresses=self.hosts,
            object_group=input('Enter object-group ID: ')
        )
        return return_template

    def render_outbound_wl(self, environment, service):
        obapi_template = self.jinjenv.get_template('two_tier.j2')
        if environment == 'PD':
            self.tier_two_asa = 'S1PDDZFWC1N1'
            if service == 'API':
                self.object_group_tier1 = 'GO-EXT-PDAPI'
                self.object_group_tier2 = 'GO-EXT-PDAPI'
            elif service == 'SFTP':
                self.object_group_tier1 = 'GO-EXT-PDOBFTS-SFTP'
                self.object_group_tier2 = 'GO-EXT-PDSFTP'

        elif environment == 'CV':
            self.tier_two_asa = 'S1Z5CVDZFWC1'
            if service == 'API':
                self.object_group_tier1 = 'GO-EXT-UAAPI'
                self.object_group_tier1 = 'GO-EXT-UAAPI'
        return_template = obapi_template.render(
            ticket_number=self.ticket_number,
            client_code=self.client_code,
            host_list=self.hosts,
            tier_two_asa=self.tier_two_asa,
            object_group_tier1=self.object_group_tier1,
            object_group_tier2=self.object_group_tier2

        )
        return return_template

    def write_out_file(self, template):
        with open(self.out_file, 'w+') as out_file:
            out_file.write(template)


obj = Templater()
obj.write_out_file(obj.render_outbound_wl('PD', 'API'))