# -*- coding: utf-8 -*-
#
# This file is part of django-xmpp-register (https://account.jabber.at/doc).
#
# django-xmpp-register is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# django-xmpp-register is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# django-xmpp-register.  If not, see <http://www.gnu.org/licenses/>.
#
# This module is copied directly from here:
#
#   http://stackoverflow.com/questions/3514342/validating-an-xmpp-jid-with-python

import re
import socket
import encodings.idna
import stringprep

from django.utils import six

# These characters aren't allowed in domain names that are used
# in XMPP
BAD_DOMAIN_ASCII = "".join([chr(c) for c in list(range(0,0x2d)) +
                    [0x2e, 0x2f] +
                    list(range(0x3a,0x41)) +
                    list(range(0x5b,0x61)) +
                    list(range(0x7b, 0x80))])

# check bi-directional character validity
def bidi(chars):
    RandAL = map(stringprep.in_table_d1, chars)
    for c in RandAL:
        if c:
            # There is a RandAL char in the string. Must perform further
            # tests:
            # 1) The characters in section 5.8 MUST be prohibited.
            # This is table C.8, which was already checked
            # 2) If a string contains any RandALCat character, the string
            # MUST NOT contain any LCat character.
            if filter(stringprep.in_table_d2, chars):
                raise UnicodeError("Violation of BIDI requirement 2")

            # 3) If a string contains any RandALCat character, a
            # RandALCat character MUST be the first character of the
            # string, and a RandALCat character MUST be the last
            # character of the string.
            if not RandAL[0] or not RandAL[-1]:
                raise UnicodeError("Violation of BIDI requirement 3")

def nodeprep(u):
    chars = list(six.text_type(u))
    i = 0
    while i < len(chars):
        c = chars[i]
        # map to nothing
        if stringprep.in_table_b1(c):
            del chars[i]
        else:
            # case fold
            chars[i] = stringprep.map_table_b2(c)
            i += 1
    # NFKC
    chars = stringprep.unicodedata.normalize("NFKC", "".join(chars))
    for c in chars:
        if (stringprep.in_table_c11(c) or
            stringprep.in_table_c12(c) or
            stringprep.in_table_c21(c) or
            stringprep.in_table_c22(c) or
            stringprep.in_table_c3(c) or
            stringprep.in_table_c4(c) or
            stringprep.in_table_c5(c) or
            stringprep.in_table_c6(c) or
            stringprep.in_table_c7(c) or
            stringprep.in_table_c8(c) or
            stringprep.in_table_c9(c) or
            c in "\"&'/:<>@"):
            raise UnicodeError("Invalid node character")

    bidi(chars)

    return chars

def resourceprep(res):
    chars = list(six.text_type(res))
    i = 0
    while i < len(chars):
        c = chars[i]
        # map to nothing
        if stringprep.in_table_b1(c):
            del chars[i]
        else:
            i += 1
    # NFKC
    chars = stringprep.unicodedata.normalize("NFKC", "".join(chars))
    for c in chars:
        if (stringprep.in_table_c12(c) or
            stringprep.in_table_c21(c) or
            stringprep.in_table_c22(c) or
            stringprep.in_table_c3(c) or
            stringprep.in_table_c4(c) or
            stringprep.in_table_c5(c) or
            stringprep.in_table_c6(c) or
            stringprep.in_table_c7(c) or
            stringprep.in_table_c8(c) or
            stringprep.in_table_c9(c)):
            raise UnicodeError("Invalid node character")

    bidi(chars)

    return chars

def parse_jid(jid):
    # first pass
    m = re.match("^(?:([^\"&'/:<>@]{1,1023})@)?([^/@]{1,1023})(?:/(.{1,1023}))?$", jid)
    if not m:
        return False

    (node, domain, resource) = m.groups()
    try:
        # ipv4 address?
        socket.inet_pton(socket.AF_INET, domain)
    except socket.error:
        # ipv6 address?
        try:
            socket.inet_pton(socket.AF_INET6, domain)
        except socket.error:
            # domain name
            dom = []
            for label in domain.split("."):
                try:
                    label = encodings.idna.nameprep(six.text_type(label))
                    encodings.idna.ToASCII(label)
                except UnicodeError:
                    return False

                # UseSTD3ASCIIRules is set, but Python's nameprep doesn't enforce it.
                # a) Verify the absence of non-LDH ASCII code points; that is, the
                for c in label:
                    if c in BAD_DOMAIN_ASCII:
                        return False
                # Verify the absence of leading and trailing hyphen-minus
                if label[0] == '-' or label[-1] == "-":
                    return False
                dom.append(label)
            domain = ".".join(dom)
    try:
        if node is not None:
            node = nodeprep(node)
        if resource is not None:
            resource = resourceprep(resource)
    except UnicodeError:
        return False

    return node, domain, resource
