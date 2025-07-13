API Reference
=============

.. contents:: Table of Contents
   :depth: 2
   :local:

Core Modules
------------

.. automodule:: logicpwn.core.auth
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: logicpwn.core.runner
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: logicpwn.core.validator
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: logicpwn.core.utils
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: logicpwn.core.async_runner
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: logicpwn.core.config
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: logicpwn.core.logging_utils
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: logicpwn.core.middleware
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: logicpwn.core.cache
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: logicpwn.core.performance
   :members:
   :undoc-members:
   :show-inheritance:

Models
------

.. automodule:: logicpwn.models.request_result
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: logicpwn.models.request_config
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: logicpwn.models
   :members:
   :undoc-members:
   :show-inheritance:

Exceptions
----------

.. automodule:: logicpwn.exceptions
   :members:
   :undoc-members:
   :show-inheritance:

Recent Improvements
------------------

Core Module Refactoring
~~~~~~~~~~~~~~~~~~~~~~

The core modules have been refactored to improve code quality and interoperability:

- **Shared Utilities**: Common functionality moved to `logicpwn.core.utils`
- **Enhanced Error Handling**: Standardized exception handling across modules
- **Secure Logging**: URL sanitization and response size logging
- **Test Reliability**: All tests now pass with improved mock handling

Authentication Module
~~~~~~~~~~~~~~~~~~~

The authentication module has been enhanced with:

- **Unified Validation**: Uses shared utilities for indicator checking
- **Improved Error Messages**: Clear, specific error messages
- **Secure Logging**: Automatic credential redaction
- **Better Session Management**: Enhanced session validation and persistence

Request Runner Module
~~~~~~~~~~~~~~~~~~~~

The request runner module includes:

- **Enhanced Error Handling**: Proper HTTP error status code handling
- **Secure Logging**: URL sanitization and response size logging
- **Improved Mock Support**: Better handling of mock objects in tests
- **Standardized Configuration**: Consistent config validation across modules

Response Validator Module
~~~~~~~~~~~~~~~~~~~~~~~~

The validator module features:

- **Unified Validation Logic**: Shared utilities for indicator checking
- **Improved Confidence Scoring**: Lowered default threshold for better validation
- **Enhanced Pattern Detection**: Better regex pattern handling
- **Comprehensive Error Handling**: Robust error handling for all validation types 