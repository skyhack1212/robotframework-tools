# robotframework-tools
#
# Tools for Robot Framework and Test Libraries.
#
# Copyright (C) 2013 Stefan Zimmermann <zimmermann.code@gmail.com>
#
# robotframework-tools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# robotframework-tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with robotframework-tools. If not, see <http://www.gnu.org/licenses/>.

"""robottools.library.keywords

Everything related to testlibrary's Keyword handling.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['Keyword',
  # from .utils:
  'KeywordName', 'KeywordsDict',
  # from .deco:
  'KeywordDecoratorType',
  # from .errors:
  'InvalidKeywordOption', 'KeywordNotDefined']

from itertools import chain

from .errors import InvalidKeywordOption, KeywordNotDefined
from .utils import KeywordName, KeywordsDict
from .deco import KeywordDecoratorType


class Keyword(object):
    """The Keyword handler for Test Library instances.

    - Provides inspection of names, args and docs.
    - Gets called by Test Library's run_keyword().
    """
    def __init__(self, name, func, libinstance):
        """Initialize with Keyword's display `name`,
           the actual Keyword `func` and the Test Library instance.
        """
        self.name = name
        self.func = func
        self.libinstance = libinstance
        # Get all ContextHandler classes for which this Keyword
        #  has context-specific implementations,
        #  to implicitly provide additional <context>= switching kwargs:
        self.context_handlers = set(ctx.handler for ctx in func.contexts)

    @property
    def __doc__(self):
        return self.func.__doc__

    @property
    def libname(self):
        """The Test Library's class and display name.
        """
        return type(self.libinstance).__name__

    @property
    def longname(self):
        """The Keyword's full display name (TestLibraryName.Keyword Name).
        """
        return '%s.%s' % (self.libname, self.name)

    def args(self):
        """Iterate the Keyword's argument spec in Robot's Dynamic API style,
           usable by Test Library's get_keyword_arguments().
        """
        # First look for custom override args list:
        if self.func.args:
            for arg in self.func.args:
                yield arg
            return
        # Then fall back to the Keyword function's implicit argspec
        #  generated by Test Library's @keyword decorator:
        argspec = self.func.argspec
        posargs = argspec.args[1:]
        defaults = argspec.defaults
        if defaults:
            for arg, defaults_index in zip(
              posargs, range(-len(posargs), 0)
              ):
                try:
                    default = defaults[defaults_index]
                except IndexError:
                    yield arg
                else:
                    yield '%s=%s' % (arg, default)
        else:
            for arg in posargs:
                yield arg
        if argspec.varargs:
            yield '*' + argspec.varargs
        if argspec.keywords:
            yield '**' + argspec.keywords
        # If the Library has session handlers
        #  or if there are context specific Keyword implementations
        #  then always provide **kwargs
        #  to support explicit <session>= and <context>= switching
        #  for single Keyword calls:
        elif self.libinstance.session_handlers or self.context_handlers:
            yield '**options'

    def __call__(self, *args, **kwargs):
        """Call the Keyword's function with the given arguments.
        """
        func = self.func
        # Look for explicit <session>= and <context>= switching options
        #  in kwargs and store the currently active
        #  session aliases and context names
        #  for switching back after the Keyword call:
        current_sessions = {}
        for _, hcls in self.libinstance.session_handlers:
            identifier = hcls.meta.identifier_name
            plural_identifier = hcls.meta.plural_identifier_name
            try:
                sname = kwargs.pop(identifier)
            except KeyError:
                pass
            else:
                current_sessions[identifier, plural_identifier] = getattr(
                  self.libinstance, identifier)
                print "Switch session: " + sname
                getattr(self.libinstance, 'switch_' + identifier)(sname)
        current_contexts = {}
        for hcls in self.context_handlers:
            identifier = hcls.__name__.lower()
            try:
                ctxname = kwargs.pop(identifier)
            except KeyError:
                pass
            else:
                current_contexts[identifier] = getattr(
                  self.libinstance, identifier)
                print "Switch context: " + ctxname
                getattr(self.libinstance, 'switch_' + identifier)(ctxname)
        # Look for context specific implementation of the Keyword function:
        for context, context_func in func.contexts.items():
            if context in self.libinstance.contexts:
                func = context_func
        # Does the keyword support **kwargs?
        if self.func.argspec.keywords or not kwargs:
            result = func(self.libinstance, *args, **kwargs)
        else: # Pass them as *varargs in 'key=value' style to the Keyword:
            ikwargs = ('%s=%s' % item for item in kwargs.items())
            result = func(self.libinstance, *chain(args, ikwargs))
        # Switch back contexts and sessions (reverse order):
        for identifier, ctxname in current_contexts.items():
            getattr(self.libinstance, 'switch_' + identifier)(ctxname)
        for (identifier, plural_identifier), session \
          in current_sessions.items():
            for sname, s in getattr(
              self.libinstance, plural_identifier
              ).items():
                if s is session:
                    getattr(self.libinstance, 'switch_' + identifier)(sname)
        return result

    def __repr__(self):
        return '%s [ %s ]' % (self.longname, ' | '.join(self.args()))
