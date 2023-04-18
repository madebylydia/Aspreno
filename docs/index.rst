Aspreno: Global error handler & self-handled error
==================================================

Aspreno is an incredible Python global error handler that helps you catch error raised in your code using an easy code style.
It also provides self-handled exceptions.

*There's no way it's "that" incredible...*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Lemme right your wrongs, old man!
Surely, this method of handling errors is pretty hacky and is not recommended in all use cases (And it's brand new tech here! Except bugs ;))
It is just (in my very personal opinion), a much better way to handle exceptions!

So check this out, **global error handling**:

.. code-block:: py

   import logging
   from aspreno import register_global_handler, ExceptionHandler

   class MyExceptionHandler(ExceptionHandler):
       def __init__(self, logging):
           self.log = logging
           # Do stuff here, basically initialize the class like usual!
    
       # This is where the magic happens!
       def handle(self, error: BaseException, **kwargs: typing.Any):
           if isinstance(error, ValueError):
               self.log.critical(f"Ooch! We just got a ValueError exception! It was raised with args: {error.args}")
               return
           
           # No need to treat the other exceptions? Leave it back to the default exception hook!
           return super().__init__(error, **kwargs)


   exception_handler = MyExceptionHandler(logging.getLogger("my_app"))
   register_global_handler(exception_handler)

   # And boom! All exceptions will now go through your "handle" method of your exception handler!
   # Pretty amazing stuff, right?

   raise ValueError("Oh no!")
   # In our logs, we would see:
   # "Ooch! We just got a ValueError exception! It was raised with args: ("Oh no!",)""


*Fair... And what about self-handled exceptions?*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Even more awesome!
Self-handled exceptions are exception *you* create (That means you can't self-handle builtin exceptions) exception that implements a "handle" method, and that can treat themselves how to resolve the error

Enough! Example please!

Let's assume we're working with an API:

.. code-block:: py

   class UnauthorizedError(Exception):
       def __init__(self, reason: str):
           self.reason = reason

       def handle(self, **kwargs: typing.Any):
           return {
               "status": "401",
               "reason": self.reason
           }


   class MyAPI:

       def execute_request(self, request: typing.Any):
           try:
               # Write your logic to *treat* requests
           except Exception as exception:
               # Does the exception have a "handle" method?
               if hasattr(exception, "handle"):
                   # Yep! It totally does!
                   exception.handle(**{"data": data})
                   # As we let the issue handle itself, we also pass it additional data through kwargs.

That's not interesting... I still have to handle that error! I could do that myself!
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Very very correct! But here's what can get your interest...
You can add all self-handled exceptions in a special folders where Aspreno will automatically add them!

So we made an *exception handler* for you to use!
So how does that look in the end?

You basically just have to create an exception manager, create your self-handled exceptions in a folder, indicates them to your exception manager, and boom!

.. code-block:: py

   from aspreno import ExceptionManager, register_global_handler

   manager = ExceptionManager()
   manager.set_exceptions_folder("path/to/folder")

   register_global_handler(manager)

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   pages/guides
   pages/information_about_aspreno


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
