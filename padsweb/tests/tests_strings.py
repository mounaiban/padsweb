#
#
# Public Archive of Days Since Timers
# PADSStringsDictionary Class Essential Tests
#
#

# Imports
from django.test import TestCase
from padsweb.strings import PADSStringDictionary
import copy

class StringDictionaryBasicTests(TestCase):
	
	def test_description_matches(self):
		# Arrangements
		sd_test_desc = 'Wordless dictionary'
		sd_test = PADSStringDictionary(dict(), sd_test_desc)
		
		# Assertions
		self.assertEquals(sd_test.description, sd_test_desc)
	
	def test_get_string_valid(self):
		# Arrangements
		dict_init = {
			'string1' : 'hood',
			'string2' : 'color',
			}
		dict_init_desc = 'Test dictionary (en-us)'
		sd_test = PADSStringDictionary(dict_init, dict_init_desc)
		
		# Assertions
		self.assertEquals(sd_test['string1'], 'hood')
		
	def test_get_string_invalid(self):
		# Arrangements
		dict_init = {'string1' : 'hood'}
		dict_init_desc = 'Test dictionary (en-us)'
		sd_test = PADSStringDictionary(dict_init, dict_init_desc)		
		
		# Assertions
		# self.assertRaises(KeyError, sd_test['invalid']) will not work
		# See: https://stackoverflow.com/a/3877187
		self.assertRaises(KeyError, sd_test.__getitem__, 'invalid')

	def test_get_string_patch_1_valid(self):
		"""One-level simple patching: one level SD patched with one level
		SD. One String added and one string replaced
		"""
		# Arrangements
		dict_init_desc = 'Test Dictionary (en-us)'
		dict_init = {
			'string1' : 'rainbow',
			'string2' : 'color',
			}
		dict_patch_desc = 'Test Dictionary (en-uk)'
		dict_patch= {
			'string1' : 'rainbow',
			'string2' : 'colour',
			'string3' : 'mate',
			}
		sd_test_init = PADSStringDictionary(dict_init, dict_init_desc)
		sd_test_patch = PADSStringDictionary(dict_patch, dict_patch_desc)
		
		# Actions
		sd_test_init.patch(sd_test_patch)
		
		# Assertions
		self.assertEqual(sd_test_init['string1'], 'rainbow')
		self.assertEqual(sd_test_init['string2'], 'colour')
		self.assertEqual(sd_test_init['string3'], 'mate')
		self.assertNotEqual(sd_test_init.description, dict_init_desc)

	def test_get_string_patch_1_empty_invalid(self):
		"""One-level simple patching, invalid reference test
		"""
		# Arrangements
		dict_init_desc = 'Wordless Dictionary'
		dict_patch_desc = 'Wordless Dictionary 2'
		
		sd_test_init = PADSStringDictionary(dict(), dict_init_desc)
		sd_test_patch = PADSStringDictionary(dict(), dict_patch_desc)
		
		# Actions
		sd_test_init.patch(sd_test_patch)
		
		# Assertions
		self.assertRaises(KeyError, sd_test_init.__getitem__, 'any_string')


class StringDictionaryExtendedTests(TestCase):
	
	@classmethod
	def setUpTestData(cls):
		"""
		Extended Tests Data
		"""
		# Arrangements
		dict_init_en_uk_desc = 'Initial Dictionary (en-uk)'
		dict_init_en_uk = {
			'string1' : 'Cadbury',
			'string2' : 'Guinness',
			}
		cls.sd_init = PADSStringDictionary(
			dict_init_en_uk, dict_init_en_uk_desc)
	
	def test_get_string_patch_replace_1_1_valid(self):
		"""
		Patch String Replacement Test
		Patching with a patched dictionary.
		The Patch is in turn patched to Level 1.
		The Patch is inserted at the original Dictionary's Level 1
		"""
		# Arrangements
		dict_repl_en_au_desc = 'Level 1 Replacement Patch (en-au)'
		dict_repl_en_au = {
			'string2' : 'VB',
			}
		dict_repl_en_nz_desc = 'Level 2 Replacement Patch (en-nz)'
		dict_repl_en_nz = {
			'string2' : 'Steinlager',
			}
		sd_replace_a = PADSStringDictionary(
			dict_repl_en_au, dict_repl_en_au_desc)
		sd_replace_n = PADSStringDictionary(
			dict_repl_en_nz, dict_repl_en_nz_desc)
		
		# Actions
		#  Replacement patching is non-commutative. Patching both ways
		#  have to be tested
		#
		#  Test A: Create an en-au patch, then patch it into the en-nz patch.
		#  Patch the en-uk StringDictionary with the resulting patch.
		sd_patch_a_n = copy.deepcopy(sd_replace_a)
		sd_patch_a_n.patch(sd_replace_n)
		sd_test_repl_a_n = copy.deepcopy(self.sd_init)
		sd_test_repl_a_n.patch(sd_patch_a_n)
		
		#  Test N: Create an en-nz patch, then patch it into the en-au patch.
		#  Patch the en-uk StringDictionary with the resulting patch.
		sd_patch_n_a = copy.deepcopy(sd_replace_a)
		sd_patch_n_a.patch(sd_replace_a)
		sd_test_repl_n_a = copy.deepcopy(self.sd_init)
		sd_test_repl_n_a.patch(sd_patch_n_a)
		
		# Assertions
		#  The SD in Test A should contain values from the en-nz and 
		#  en-uk SD's only.
		self.assertEquals(sd_test_repl_a_n['string1'], 'Cadbury')
		self.assertEquals(sd_test_repl_a_n['string2'], 'Steinlager')
		self.assertFalse(sd_test_repl_a_n.infinite_loop)
		
		#  The SD in Test B should contain values from the en-au and
		#  en-uk SD's only.
		self.assertEquals(sd_test_repl_n_a['string1'], 'Cadbury')
		self.assertEquals(sd_test_repl_n_a['string2'], 'VB')
		self.assertFalse(sd_test_repl_a_n.infinite_loop)

	def test_get_string_patch_expand_1_1_valid(self):
		"""Patch String Expansion Test
		Patching with a patched dictionary.
		The Patch is in turn patched to Level 1.
		The Patch is inserted at the original Dictionary's Level 1
		"""	
		# Arrangements
		dict_exp_en_in_desc = 'Level 1 Expansion Patch (en-in)'
		dict_exp_en_in = {
			'string3' : 'Britannia',
			}
		dict_exp_en_sg_desc = 'Level 2 Expansion Patch (en-sg)'
		dict_exp_en_sg = {
			'string4' : '100 Plus',
			}
		sd_expand_i = PADSStringDictionary(dict_exp_en_in, 
			dict_exp_en_in_desc)
		sd_expand_s = PADSStringDictionary(dict_exp_en_sg, 
			dict_exp_en_sg_desc)
		
		# Actions
		#  Expansion patching is commutative.
		#  The order of patching is expected to produce the same result
		sd_patch_s_i = copy.deepcopy(sd_expand_s)
		sd_patch_s_i.patch(sd_expand_i)
		sd_test_exp_s_i = copy.deepcopy(self.sd_init)
		sd_test_exp_s_i.patch(sd_patch_s_i)
		
		# Assertions
		#  The SD in this test should contain values from the en-uk, 
		#  en-in and en-sg dictionaries
		self.assertEquals(sd_test_exp_s_i['string1'], 'Cadbury')
		self.assertEquals(sd_test_exp_s_i['string2'], 'Guinness')
		self.assertEquals(sd_test_exp_s_i['string3'], 'Britannia')
		self.assertEquals(sd_test_exp_s_i['string4'], '100 Plus')
		self.assertFalse(sd_test_exp_s_i.infinite_loop)

	def test_get_string_patch_1_1_invalid(self):
		# Arrangements
		dict_exp_en_us_desc = 'Level 1 Expansion Patch (en-us)'
		dict_exp_en_us = {
			'string101' : 'Pepsi',
			}
		dict_exp_en_ca_desc = 'Level 2 Expansion Patch (en-ca)'
		dict_exp_en_ca = {
			'string102' : 'Fox\'s',
			}
		sd_expand_u = PADSStringDictionary(dict_exp_en_us, 
			dict_exp_en_us_desc)
		sd_expand_c = PADSStringDictionary(dict_exp_en_ca, 
			dict_exp_en_ca_desc)
		
		# Actions
		#  Patch en-us dictionary to en-ca, then use result to patch
		#  the original en-uk dictionary.
		sd_patch_u_c = copy.deepcopy(sd_expand_u)
		sd_patch_u_c.patch(sd_expand_c)
		sd_test_exp_u_c = copy.deepcopy(self.sd_init)
		sd_test_exp_u_c.patch(sd_patch_u_c)
		
		# Assertions
		self.assertRaises(KeyError, sd_test_exp_u_c.__getitem__, 'non_existent')
		self.assertFalse(sd_test_exp_u_c.infinite_loop)
		
	def test_infinite_loop_1_1_flagged(self):
		# Arrangements
		sd_test_infi_loop = copy.deepcopy(self.sd_init)

		dict_patch_bad_desc = 'Wordless Dictionary'
		sd_patch_bad = PADSStringDictionary(dict(), dict_patch_bad_desc)
		sd_patch_bad.patch(sd_test_infi_loop)

		sd_test_infi_loop.patch(sd_patch_bad)
		
		# Assertions
		#  This lookup is just to trigger the recursion infinite loop 
		#  and associated RecursionError
		self.assertRaises(KeyError, sd_patch_bad.__getitem__, 'non_existent')
		self.assertTrue(sd_patch_bad.infinite_loop)
	
	def test_patch_with_self_flagged(self):
		# Actions
		sd_test_self_patch = copy.deepcopy(self.sd_init)
		sd_test_self_patch.patch(sd_test_self_patch)
		
		# Assertions
		self.assertEqual(sd_test_self_patch.get_patch_level(), 0)

