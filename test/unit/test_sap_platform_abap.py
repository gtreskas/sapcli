#!/usr/bin/env python3

import unittest
from io import StringIO

import sap.platform.abap
from sap.platform.abap import StringTable


class PLAIN_STRUCT(sap.platform.abap.Structure):

    PYTHON: str
    LINUX: str


class PLAIN_STRUCT_TT(sap.platform.abap.InternalTable[PLAIN_STRUCT]):

    pass


class STRUCT_WITH_STRING_TABLE(sap.platform.abap.Structure):

    PYTHON: str
    LINUX: str
    DISTROS: sap.platform.abap.StringTable


class TestSAPPlatformABAP(unittest.TestCase):

    def test_structure_init_without_values(self):
        plain = PLAIN_STRUCT()

        self.assertIsNone(plain.PYTHON)
        self.assertIsNone(plain.LINUX)

    def test_structure_init_with_all_values(self):
        plain = PLAIN_STRUCT(PYTHON='3.7', LINUX='Fedora')

        self.assertEqual(plain.PYTHON, '3.7')
        self.assertEqual(plain.LINUX, 'Fedora')

    def test_structure_init_with_some_values(self):
        plain = PLAIN_STRUCT(PYTHON='3.7')

        self.assertEqual(plain.PYTHON, '3.7')
        self.assertEqual(plain.LINUX, None)

        plain = PLAIN_STRUCT(LINUX='Fedora')

        self.assertEqual(plain.PYTHON, None)
        self.assertEqual(plain.LINUX, 'Fedora')

    def test_structure_init_with_extra_values(self):
        with self.assertRaises(TypeError) as caught:
            plain = PLAIN_STRUCT(JAVASCRIPT='@')

        self.assertEqual(str(caught.exception), 'PLAIN_STRUCT does not define member JAVASCRIPT')

    def test_internal_table_without_params(self):
        table = PLAIN_STRUCT_TT()

        self.assertEqual(table._type, PLAIN_STRUCT)
        self.assertEqual(len(table), 0)

    def test_internal_table_with_one_row_param(self):
        table = PLAIN_STRUCT_TT(PLAIN_STRUCT(PYTHON='3.7', LINUX='4.20'))

        self.assertEqual(len(table), 1)

        self.assertEqual(table[0].PYTHON, '3.7')
        self.assertEqual(table[0].LINUX, '4.20')

    def test_internal_table_with_one_list_row_param(self):
        table = PLAIN_STRUCT_TT([PLAIN_STRUCT(PYTHON='3.7', LINUX='4.20')])

        self.assertEqual(len(table), 1)

        self.assertEqual(table[0].PYTHON, '3.7')
        self.assertEqual(table[0].LINUX, '4.20')

    def test_internal_table_with_one_table_param(self):
        table = PLAIN_STRUCT_TT(PLAIN_STRUCT_TT(PLAIN_STRUCT(PYTHON='3.7', LINUX='4.20')))

        self.assertEqual(len(table), 1)

        self.assertEqual(table[0].PYTHON, '3.7')
        self.assertEqual(table[0].LINUX, '4.20')

    def test_internal_table_with_params(self):
        table = PLAIN_STRUCT_TT(
            PLAIN_STRUCT(PYTHON='3.7', LINUX='4.20'),
            PLAIN_STRUCT(PYTHON='3.6', LINUX='4.19'))

        self.assertEqual(len(table), 2)

        self.assertEqual(table[0].PYTHON, '3.7')
        self.assertEqual(table[0].LINUX, '4.20')

        self.assertEqual(table[1].PYTHON, '3.6')
        self.assertEqual(table[1].LINUX, '4.19')

    def test_internal_table_invalid_params(self):
        with self.assertRaises(TypeError) as caught_table_typemismatch:
            PLAIN_STRUCT_TT(StringTable('foo'))

        self.assertEqual(str(caught_table_typemismatch.exception), 'cannot copy InternalTable of type str')

        with self.assertRaises(TypeError) as caught_row_typemismatch:
            PLAIN_STRUCT_TT('foo')

        self.assertEqual(str(caught_row_typemismatch.exception), 'type of appended value str does not match table type PLAIN_STRUCT')

        with self.assertRaises(TypeError) as caught_tworow_typemismatch:
            PLAIN_STRUCT_TT('foo', 'bar')

        self.assertEqual(str(caught_tworow_typemismatch.exception), 'type of appended value str does not match table type PLAIN_STRUCT')

        with self.assertRaises(TypeError) as caught_list_typemismatch:
            PLAIN_STRUCT_TT(['foo', 'bar'])

        self.assertEqual(str(caught_list_typemismatch.exception), 'type of appended value str does not match table type PLAIN_STRUCT')


    def test_internal_table_append_kwargs(self):
        table = PLAIN_STRUCT_TT()
        table.append(PYTHON='3.7', LINUX='4.20')

        self.assertEqual(len(table), 1)

        self.assertEqual(table[0].PYTHON, '3.7')
        self.assertEqual(table[0].LINUX, '4.20')

    def test_internal_table_append_row(self):
        table = PLAIN_STRUCT_TT()
        table.append(PLAIN_STRUCT(PYTHON='3.7', LINUX='4.20'))

        self.assertEqual(len(table), 1)

        self.assertEqual(table[0].PYTHON, '3.7')
        self.assertEqual(table[0].LINUX, '4.20')

    def test_internal_table_append_invalid(self):
        table = PLAIN_STRUCT_TT()

        with self.assertRaises(TypeError) as caught_mixing:
            table.append(PLAIN_STRUCT(), PYTHON='3.7')

        self.assertEqual(len(table), 0)
        self.assertEqual(str(caught_mixing.exception), 'cannot mix positional and keyword parameters')

        with self.assertRaises(TypeError) as caught_noargs:
            table.append()

        self.assertEqual(len(table), 0)
        self.assertEqual(str(caught_noargs.exception), 'no parameters given')

        with self.assertRaises(TypeError) as caught_onlyone:
            table.append(PLAIN_STRUCT(), PLAIN_STRUCT())

        self.assertEqual(len(table), 0)
        self.assertEqual(str(caught_onlyone.exception), 'append accepts only one positional argument but 2 were given')

        with self.assertRaises(TypeError) as caught_invalid:
            table.append('foo')

        self.assertEqual(len(table), 0)
        self.assertEqual(str(caught_invalid.exception), 'type of appended value str does not match table type PLAIN_STRUCT')


class TestSAPPlatformABAPToXML(unittest.TestCase):

    def test_to_xml_plain_stucture(self):
        struct = PLAIN_STRUCT(PYTHON='theBest', LINUX='better')

        dest = StringIO()
        sap.platform.abap.to_xml(struct, dest)

        self.assertEqual(dest.getvalue(), '''<?xml version="1.0" encoding="utf-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
 <asx:values>
  <PLAIN_STRUCT>
   <PYTHON>theBest</PYTHON>
   <LINUX>better</LINUX>
  </PLAIN_STRUCT>
 </asx:values>
</asx:abap>\n''')

    def test_to_xml_plain_stucture_changed_top(self):
        struct = PLAIN_STRUCT(PYTHON='theBest', LINUX='better')

        dest = StringIO()
        sap.platform.abap.to_xml(struct, dest, top_element='ROOT')

        self.assertEqual(dest.getvalue(), '''<?xml version="1.0" encoding="utf-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
 <asx:values>
  <ROOT>
   <PYTHON>theBest</PYTHON>
   <LINUX>better</LINUX>
  </ROOT>
 </asx:values>
</asx:abap>\n''')

    def test_to_xml_stucture_with_string_table(self):
        struct = STRUCT_WITH_STRING_TABLE(PYTHON='theBest', LINUX='better',
                                          DISTROS=StringTable('Fedora', 'CentOS'))

        dest = StringIO()
        sap.platform.abap.to_xml(struct, dest)

        self.assertEqual(dest.getvalue(), '''<?xml version="1.0" encoding="utf-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
 <asx:values>
  <STRUCT_WITH_STRING_TABLE>
   <PYTHON>theBest</PYTHON>
   <LINUX>better</LINUX>
   <DISTROS>
    <item>Fedora</item>
    <item>CentOS</item>
   </DISTROS>
  </STRUCT_WITH_STRING_TABLE>
 </asx:values>
</asx:abap>\n''')

    def test_to_xml_internal_table_of_structure(self):
        lines = PLAIN_STRUCT_TT()

        lines.append(PYTHON='Nice', LINUX='Awesome')
        lines.append(PYTHON='Cool', LINUX='Fabulous')

        dest = StringIO()
        sap.platform.abap.to_xml(lines, dest)

        self.maxDiff = None
        self.assertEqual(dest.getvalue(), '''<?xml version="1.0" encoding="utf-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
 <asx:values>
  <PLAIN_STRUCT_TT>
   <PLAIN_STRUCT>
    <PYTHON>Nice</PYTHON>
    <LINUX>Awesome</LINUX>
   </PLAIN_STRUCT>
   <PLAIN_STRUCT>
    <PYTHON>Cool</PYTHON>
    <LINUX>Fabulous</LINUX>
   </PLAIN_STRUCT>
  </PLAIN_STRUCT_TT>
 </asx:values>
</asx:abap>\n''')

    def test_to_xml_internal_table_of_structure_with_own_element(self):
        lines = PLAIN_STRUCT_TT()

        lines.append(PYTHON='Nice', LINUX='Awesome')
        lines.append(PYTHON='Cool', LINUX='Fabulous')

        dest = StringIO()
        sap.platform.abap.XMLSerializers.abap_to_xml(lines, dest, '', row_name_getter=lambda x: 'item')

        self.maxDiff = None
        self.assertEqual(dest.getvalue(), '''<PLAIN_STRUCT_TT>
 <item>
  <PYTHON>Nice</PYTHON>
  <LINUX>Awesome</LINUX>
 </item>
 <item>
  <PYTHON>Cool</PYTHON>
  <LINUX>Fabulous</LINUX>
 </item>
</PLAIN_STRUCT_TT>
''')


if __name__ == '__main__':
    unittest.main()
