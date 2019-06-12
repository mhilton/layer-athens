import base64
import os

import requests

from charmhelpers.core.hookenv import (
    application_version_set,
    charm_dir,
    config,
    open_port,
    status_set,
)
from charmhelpers.core.host import write_file
from charms.docker import Compose
from charms.reactive import (
    clear_flag,
    set_flag,
    when,
    when_any,
    when_file_changed,
    when_not,
)


@when('docker.available')
@when_not('athens.up')
def start():
    compose()


@when_file_changed(os.path.join(charm_dir(), 'docker-compose.yaml'))
def docker_compose_changed():
    set_flag('athens.restart')


@when('athens.up')
@when_not('athens.port.open')
def config_port():
    open_port(3000)
    set_flag('athens.port.open')


@when_any(
    'config.changed.athens-image',
    'config.changed.http_proxy',
    'config.changed.https_proxy',
    'config.changed.no_proxy')
def config_changed():
    set_flag('athens.restart')


@when('config.changed.netrc')
def config_changed_netrc():
    write_file('/srv/athens/netrc', base64.b64decode(config()['netrc']))
    set_flag('athens.restart')


@when('athens.up')
@when('athens.restart')
def compose():
    '''compose brings up the athens service.'''
    status_set('maintenance', 'docker-compose up athens')
    os.environ['athens_image'] = config()['athens-image']
    os.environ['ATHENS_DISK_STORAGE_ROOT'] = '/srv/athens/cache'
    os.environ['ATHENS_STORAGE_TYPE'] = 'disk'
    os.environ['ATHENS_NETRC_PATH'] = '/srv/athens/netrc'
    os.environ['http_proxy'] = config()['http_proxy']
    os.environ['https_proxy'] = config()['https_proxy']
    os.environ['no_proxy'] = config()['no_proxy']
    Compose(charm_dir()).up()
    clear_flag('athens.restart')
    set_flag('athens.up')
    application_version_set(
        requests.get('http://localhost:3000/version').json()['version'])
    status_set('active', 'athens running')


@when('website.available')
@when('athens.port.open')
def configure_website(website):
    website.configure(port=3000)
