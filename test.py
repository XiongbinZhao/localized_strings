import os
import localizable

strings = localizable.parse_strings(filename='/Users/jackzhao/Desktop/spc-ios/SPC/en.lproj/Localizable.strings')
for s in strings:
	for key, value in s.iteritems():
		print key + ": " + value

	print "\n"