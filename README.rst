README
######

|hacs_badge|

Installation
************
Place the ``custom_components`` folder into your configuration directory
(or add its contents to an existing ``custom_components`` folder).

Alternatively install with `HACS <https://hacs.xyz/>`_.

Authentication
**************
You will need to perform one-time authentication for the API to work.

This authentication can be performed on your local computer, or on your
home-assistant server.

.. code:: bash

    pip install hisensetv
    hisensetv 10.0.0.28 --authorize

See `newAM/hisensetv <https://github.com/newAM/hisensetv>`_ for more details.

Configuration
*************

.. code:: yaml

    switch:
      - platform: hisensetv
        host: 10.0.0.28
        mac: ab:cd:ef:12:34:56
        name: tv

Warning
*******
This is provided **as-is**.
This is my first time going this deep into homeassistant and I have no idea
if I have horribly messed something up.

.. |hacs_badge| image:: https://img.shields.io/badge/HACS-Custom-orange.svg
    :target: https://github.com/custom-components/hacs
