"""
.. module:: freezable
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module which contains the Freezable base class for blocking attribute changes.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

class Freezable:

    def __init__(self):
        object.__setattr__(self, "__frozen__", False)
        return
    
    def freeze(self):
        object.__setattr__(self, "__frozen__", True)
        return
    
    def __setattr__(self, name, value):
        # If the '__frozen__' flag exists and is True, block all changes
        if getattr(self, "__frozen__", False):
            raise AttributeError(f"Freezable objects cannot be modified after they have been initialized and frozen. name={name}")
        
        # Otherwise, allow the assignment
        object.__setattr__(self, name, value)
        return