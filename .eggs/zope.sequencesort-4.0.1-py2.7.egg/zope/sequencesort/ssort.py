##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Advanced sort support

e.g .Sort(sequence, (("akey", "nocase"), ("anotherkey", "cmp", "desc")))
"""

try:
    cmp = cmp
except NameError: #pragma NO COVER Py3k
    def cmp(lhs, rhs):
        return int(rhs < lhs) - int(lhs < rhs)

class _Smallest(object):
    """ Singleton:  sorts below any other value.
    """
    __slots__ = ()
    def __lt__(self, other):
        return True
    def __eq__(self, other):
        return other is self
    def __gt__(self, other):
        return False
_Smallest = _Smallest()

try:
    # Python 3.2+
    from functools import cmp_to_key
except ImportError: #pragma NO COVER Python 2.x
    cmp_to_key = None


def sort(sequence, sort=(), _=None, mapping=0):
    """Return a sorted copy of 'sequence'.

    - sequence is a sequence of objects to be sorted

    - sort is a sequence of tuples (key,func,direction)
      that define the sort order:

      - key is the name of an attribute to sort the objects by

      - func is the name of a comparison function. This parameter is
        optional

        allowed values:

        - "cmp" -- the standard comparison function (default)

        - "nocase" -- case-insensitive comparison

        - "strcoll" or "locale" -- locale-aware string comparison

        - "strcoll_nocase" or "locale_nocase" -- locale-aware case-insensitive
           string comparison

        - "xxx" -- a user-defined comparison function

      - direction -- defines the sort direction for the key (optional).
        (allowed values: "asc" (default) , "desc")
    """
    need_sortfunc = 0

    if sort:
        for s in sort:
            if len(s) > 1: # extended sort if there is reference to...
                # ...comparison function or sort order, even if they are
                # "cmp" and "asc"
                need_sortfunc = 1
                break

    sortfields = sort # multi sort = key1,key2
    multsort = len(sortfields) > 1 # flag: is multiple sort

    if need_sortfunc:
        # prepare the list of functions and sort order multipliers
        sf_list = make_sortfunctions(sortfields, _)

        # clean the mess a bit
        if multsort: # More than one sort key.
            sortfields = [x[0] for x in sf_list]
        else:
            sort = sf_list[0][0]

    elif sort:
        if multsort: # More than one sort key.
            sortfields = [x[0] for x in sort]
        else:
            sort = sort[0][0]

    isort = not sort

    s = []
    for client in sequence:
        k = _Smallest
        if isinstance(client, tuple) and len(client) == 2:
            if isort:
                k = client[0]
            v = client[1]
        else:
            if isort:
                k = client
            v = client

        if sort:
            if multsort: # More than one sort key.
                k = []
                for sk in sortfields:
                    try:
                        if mapping:
                            akey = v[sk]
                        else:
                            akey = getattr(v, sk)
                    except (AttributeError, KeyError):
                        akey = _Smallest
                    else:
                        if type(akey) not in BASIC_TYPES:
                            try:
                                akey = akey()
                            except:
                                pass
                    k.append(akey)
            else: # One sort key.
                try:
                    if mapping:
                        k = v[sort]
                    else:
                        k = getattr(v, sort)
                except (AttributeError, KeyError):
                    k = _Smallest
                if type(k) not in BASIC_TYPES:
                    try:
                        k = k()
                    except:
                        pass

        s.append((k,client))

    if need_sortfunc:
        by = SortBy(multsort, sf_list)
        if cmp_to_key is None:
            s.sort(by)
        else: #pragma NO COVER Py3k
            s.sort(key=cmp_to_key(by))
    else:
        s.sort()

    return [x[1] for x in s]


SortEx = sort

BASIC_TYPES = {
    type(''): 1,
    type(b''): 1,
    type(0): 1,
    type(0.0): 1,
    type(()): 1,
    type([]): 1,
    type(None) : 1,
}

try:
    unicode
except NameError: #pragma NO COVER Py3k
    pass
else: #pragma NO COVER Python 2
    BASIC_TYPES[unicode] = 1

def nocase(str1, str2):
    return cmp(str1.lower(), str2.lower())

import sys
if "locale" in sys.modules: # only if locale is already imported
    from locale import strcoll

    def strcoll_nocase(str1, str2): #pragma NO COVER XXX global locale
        return strcoll(str1.lower(), str2.lower())


def make_sortfunctions(sortfields, _):
    """Accepts a list of sort fields; splits every field, finds comparison
    function. Returns a list of 3-tuples (field, cmp_function, asc_multplier)"""

    sf_list = []
    for field in sortfields:
        info = list(field)
        i_len = len(info)

        if i_len == 1:
            info.append("cmp")
            info.append("asc")
        elif i_len == 2:
            info.append("asc")
        elif i_len == 3:
            pass
        else:
            raise SyntaxError(
                "sort option: (Key [,sorter_name [,direction]])")

        f_name = info[1]

        # predefined function?
        if f_name == "cmp":
            func = cmp # builtin
        elif f_name == "nocase":
            func = nocase
        elif f_name in ("locale", "strcoll"): #pragma NO COVER
            func = strcoll
        elif f_name in ("locale_nocase", "strcoll_nocase"): #pragma NO COVER
            func = strcoll_nocase
        else: # no - look it up in the namespace
            if hasattr(_, 'getitem'):
                # support for zope.documenttemplate.dt_util.TemplateDict
                func = _.getitem(f_name, 0)
            else:
                func = _[f_name]

        sort_order = info[2].lower()

        if sort_order == "asc":
            multiplier = +1
        elif sort_order == "desc":
            multiplier = -1
        else:
            raise SyntaxError(
                "sort direction must be either ASC or DESC")

        sf_list.append((info[0], func, multiplier))

    return sf_list


class SortBy(object):
    def __init__(self, multsort, sf_list):
        self.multsort = multsort
        self.sf_list = sf_list

    def __call__(self, o1, o2):
        n_fields = len(self.sf_list)
        if self.multsort:
            o1 = o1[0] # if multsort - take the first element (key list)
            o2 = o2[0]
            req_len = n_fields
        else:
            req_len = n_fields + 1


        # assert that o1 and o2 are tuples of apropriate length
        if len(o1) != req_len:
            raise ValueError("%s, %d" % (o1, req_len))
        if len(o2) != req_len:
            raise ValueError("%s, %d" % (o2, req_len))

        # now run through the list of functions in sf_list and
        # compare every object in o1 and o2
        for i in range(n_fields):
            # if multsort - we already extracted the key list
            # if not multsort - i is 0, and the 0th element is the key
            c1, c2 = o1[i], o2[i]
            func, multiplier = self.sf_list[i][1:3]
            n = func(c1, c2)
            if n:
                return n * multiplier

        # all functions returned 0 - identical sequences
        return 0
