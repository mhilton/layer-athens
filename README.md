Athens
======

The [Athens](https://docs.gomods.io/) go module proxy.

Configuration
-------------

These are the configuration settings that affect the athens server. Some
are taken from lower layers.

`athens-image` specifies the docker image that the charm should install.

`http_proxy` specifies the HTTP proxy used by athens.

`https_proxy` specifies the HTTPS proxy used by athens.

`netrc` specifies a base64 encoded netrc file that athens (go and git)
will use to authenticate http requests.

`no_proxy` specifies hosts that will bypass the specified proxy in
HTTP requests.
