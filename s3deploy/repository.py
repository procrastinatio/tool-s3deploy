#!/usr/bin/env python3


# see http://click.palletsprojects.com/en/7.x/complex/
# https://krzysztofzuraw.com/blog/2016/factory-pattern-python.html

import os
import json   


class BaseRepo(object):

    def __init__(self, home=None, debug=False):
        self.home = os.path.abspath(home or '.')
        self.debug = debug
        
    def generate(self):
        raise NotImplementedError()
        
    @classmethod
    def check_extenstion(cls,extension):
      return extension == cls.__name__


class SimpleRepo(BaseRepo):
     def __init__(self, home=None, debug=False):
        self.home = os.path.abspath(home or '.')
        self.debug = debug
        
     def generate(self):
        return [1,2,3]
        
    
class GeoAdminRepo(BaseRepo):
 
    def __init__(self, home=None, debug=False):
        self.home = os.path.abspath(home or '.')
        self.debug = debug
        
    def generate(self):
        return ['a', 'b', 'c']
        
        
class RepoManager(object):
    ARCHIVE_ENGINES = [SimpleRepo, GeoAdminRepo]

    def __init__(self, type, repo_home, debug):
        self.repo_home = repo_home
        self.debug = debug
        self.type = type
        self.archive_engine = self.choose_archive_engine()

    def choose_archive_engine(self):
        for engine in self.ARCHIVE_ENGINES:
            if engine.check_extenstion(self.type):
                return engine(self.repo_home, self.debug)
