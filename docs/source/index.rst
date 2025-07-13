LogicPwn Documentation
====================

LogicPwn is a comprehensive security testing framework designed for advanced business logic exploitation and multi-step attack automation. Built for penetration testing, security research, and automated vulnerability assessment.

Features
--------

Quick Start
----------

Install LogicPwn:

.. code-block:: bash

   pip install logicpwn

Basic usage:

.. code-block:: python

   from logicpwn.core import send_request, send_request_async
   from logicpwn.models import RequestResult
   
   # Synchronous request
   result = send_request(url="https://target.com/api/data", method="POST")
   
   # Async request
   async with AsyncRequestRunner() as runner:
       results = await runner.send_requests_batch(request_configs)

Advanced exploit chaining:

.. code-block:: python

   from logicpwn.core import authenticate_session, AsyncSessionManager
   
   # Authenticate and chain exploits
   session = authenticate_session(auth_config)
   response = session.get("https://target.com/admin/panel")
   response = session.post("https://target.com/api/users", data=payload)

Installation
-----------

LogicPwn requires Python 3.9+ and can be installed via pip:

.. code-block:: bash

   pip install logicpwn[async]

For development installation:

.. code-block:: bash

   git clone https://github.com/logicpwn/logicpwn.git
   cd logicpwn
   poetry install

Requirements
-----------

* Python 3.9+
* aiohttp (for async functionality)
* pydantic (for data validation)
* requests (for synchronous requests)

Documentation Structure
----------------------

* :doc:`getting_started` - Installation and basic usage
* :doc:`async_runner` - High-performance async request execution
* :doc:`api_reference` - Complete API documentation

Security Notice
--------------

LogicPwn is designed for authorized security testing only. Always ensure you have proper authorization before testing any systems. The authors are not responsible for any misuse of this tool.

License
-------

This project is licensed under the MIT License - see the LICENSE file for details.

Support
-------

* GitHub Issues: https://github.com/logicpwn/logicpwn/issues
* Documentation: https://logicpwn.readthedocs.io/
* Security: security@logicpwn.org

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

