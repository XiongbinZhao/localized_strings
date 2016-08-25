import os
import localizable

strings = localizable.parse_strings(filename='/Users/jackzhao/Desktop/localized_strings/CouponAllLoadedView.strings')
for s in strings:
	for key, value in s.iteritems():
		print key + ": " + value

	print "\n"