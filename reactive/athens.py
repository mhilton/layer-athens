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
from charms.reactive import set_flag, when, when_file_changed


@when('config.changed')
def config_changed():
    env = [
        'ATHENS_STORAGE_TYPE=disk',
        'ATHENS_DISK_STORAGE_ROOT=/srv/athens/cache']
    if os.path.exists('/srv/athens/netrc'):
        env.append('ATHENS_NETRC_PATH=/srv/athens/netrc')
    write_file('/srv/athens/env', "\n".join(env).encode('utf-8'))


@when('docker.available')
def athens_up():
    status_set('maintenance', 'docker-compose up athens')
    os.environ['athens_image'] = config()['athens-image']
    Compose(charm_dir()).up()
    set_flag("athens.up")
    application_version_set(
        requests.get('http://localhost:3000/version').json()['version'])
    status_set('active', 'athens running')


@when('athens.up')
def config_port():
    open_port(3000)


@when('athens.up')
@when_file_changed('/srv/athens/env', '/srv/athens/netrc')
def athens_config_changed():
    athens_up()


@when('athens.up')
@when('config.changed.athens-image')
def athens_image_changed():
    athens_up()


@when('config.changed.netrc')
def netrc():
    v = config()['netrc']
    if v == "" and os.path.exists('/srv/athens/netrc'):
        os.remove('/srv/athens/netrc')
    elif v != "":
        write_file('/srv/athens/netrc', base64.b64decode(v))
    config_changed()
