# NeoPI - Enhanced Web Shell Detection Tool
====================

NeoPI is a Python-based utility for detecting obfuscated and encrypted content within text/script files, with a focus on identifying hidden web shells. It uses statistical analysis and pattern matching to flag suspicious files.

## Features

- Multiple detection methods:
  - Shannon entropy analysis
  - Index of Coincidence (IC) calculation
  - Longest word/string detection
  - Compression ratio analysis
  - Signature-based pattern matching
  - Eval usage detection

- Advanced scanning modes:
  - Block-level scanning (`-b`) for granular analysis
  - Alarm mode (`-m`) for automated flagging of suspicious files
  - Unicode-aware scanning with UTF handling (`-u`)
  - Symlink following support (`-f`)

- Output options:
  - Console output with ranked results
  - CSV export support
  - Detailed statistics and scan timing

## Installation

```bash
git clone https://github.com/Neohapsis/NeoPI.git
cd NeoPI
```

## Usage

Basic usage:
```bash
./neopi.py [options] <start directory> [filename regex]
```

Common examples:
```bash
# Scan with all tests
./neopi.py -a /var/www/

# Scan PHP files with entropy and signature tests
./neopi.py -es /var/www/ "\.php$"

# Block-level scan with 512 byte blocks
./neopi.py -ab 512 /var/www/

# Alarm mode with 2.0 standard deviation threshold
./neopi.py -am 2.0 /var/www/
```

### Command Line Options

- `-a, --all`: Run all tests (entropy, longest word, IC, signatures)
- `-e, --entropy`: Run entropy test
- `-i, --ic`: Run Index of Coincidence test
- `-l, --longestword`: Run longest word test
- `-s, --signature`: Run basic signature test
- `-S, --supersignature`: Run enhanced signature test
- `-E, --eval`: Check specifically for eval() usage
- `-z, --zlib`: Run compression ratio test
- `-b BLOCKSIZE`: Enable block-level scanning
- `-m THRESHOLD`: Enable alarm mode with deviation threshold
- `-u`: Skip files with high Unicode content
- `-f`: Follow symbolic links
- `-c FILE`: Export results to CSV file

## How It Works

NeoPI employs multiple statistical and pattern-matching techniques to identify potentially malicious files:

1. **Entropy Analysis**: Measures randomness in file content
2. **Index of Coincidence**: Detects language patterns and obfuscation
3. **Longest Word**: Identifies suspiciously long strings
4. **Signature Matching**: Looks for known malicious patterns
5. **Compression Analysis**: Checks data compressibility

Results are ranked and scored to help prioritize investigation of suspicious files.

## Original Authors

- Ben Hagen (ben.hagen@neohapsis.com)
- Scott Behrens (scott.behrens@neohapsis.com)

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit pull requests.
NeoPI is a Python script that uses a variety of statistical methods to detect obfuscated and encrypted content within text/script files. The intended purpose of NeoPI is to aid in the detection of hidden web shell code. The development focus of NeoPI was creating a tool that could be used in conjunction with other established detection methods such as Linux Malware Detect or traditional signature/keyword based searches.

NeoPI recursively scans through the file system from a base directory and will rank files based on the results of  a number of tests. It also presents a “general” score derived from file rankings within the individual tests.

#Requirements
NeoPI is platform independent and can be run on any system with Python 2.6 or greater installed installed. The user running the script should have read access to all of the files that will be scanned.

#How to use it
NeoPI is platform independent and will run on both Linux and Windows.  To start using NeoPI first checkout the code from our github repository

	git clone ssh://git@github.com:Neohapsis/NeoPI.git

The small NeoPI script is now in your local directory.  We are going to go though a few examples on Linux and then switch over to Windows.  

Let’s run neopi.py with the -h flag to see the options.  

	[sbehrens@WebServer2 opt]$ ./neopi.py -h
	Usage: neopi.py [options] <start directory> <OPTIONAL: filename regex>

	Options:
	  --version             show program's version number and exit
	  -h, --help            show this help message and exit
	  -c FILECSV, --csv=FILECSV
							generate CSV outfile
	  -a, --all             Run all tests [Entropy, Longest Word, Compression
	  -e, --entropy         Run entropy Test
	  -l, --longestword     Run longest word test
	  -i, --ic              Run IC test
	  -A, --auto            Run auto file extension tests

Let’s break down the options into greater detail.

	-c FILECSV, --csv=FILECSV
This generates a CSV output file containing the results of the scan.  

	-a, --all
This runs all tests including entropy, longest word, and index of coincidence.  In general, we suggest running all tests to build the most comprehensive list of possible web shells.

	-e, --entropy
This flag can be set to run only the entropy test.  

	-l, --longestword
This flag can be set to run only the longest word test.  

	-i, --ic
This flag can be set to run only the Index of Coincidence test.  

	-A, --auto 
This flag runs an auto generated regular expression that contains many common web application file extensions.    This list is by no means comprehensive but does include a good ‘best effort’ scan if you are unsure of what web application languages your server is running.  The current list of  extensions are included below:

	valid_regex = re.compile('\.php|\.asp|\.aspx|\.sh|\.bash|\.zsh|\.csh|\.tsch|\.pl|\.py|\.txt|\.cgi|\.cfm')

Now that we are familiar with the flags and we have downloaded a copy of the script from GIT, let’s go head and run it on a web server we think may be infected with obfuscated web shells.    

	[sbehrens@WebServer2 opt]$ sudo ./neopi.py -c scan1.csv -a -A /var/www/
	
The resulst of the scan we be displayed to console as well as written to 'scan1.csv'.  Here is an example of the scan results:

	[root@WebServer2 opt]# python neopi.py -a -A /var/www/html/

	[[ Average IC for Search ]]
	0.0372337579606

	[[ Top 10 IC files ]]
	  0.0156    /var/www/html/webmedia/shell3.php
	  0.0178    /var/www/html/phpadmin/phpMyAdmin-3.3.8-all-languages/lang/chinese_simplified-utf-8.inc.php
	  0.0184    /var/www/html/wordpress/wordpress/wp-admin/weevely.php
	  0.0217    /var/www/html/joomla/templates/system/index.php
	  0.0217    /var/www/html/joomla/administrator/templates/system/index.php
	  0.0225    /var/www/html/wordpress/wordpress/wp-admin/js/revisions-js.php
	  0.0229    /var/www/html/epesiBIM/epesi-1.1.3-rev7318/modules/Base/Mail/language/phpmailer.lang-ch.php
	  0.0239    /var/www/html/epesiBIM/epesi-1.1.3-rev7318/modules/Base/Mail/language/phpmailer.lang-zh.php
	  0.0240    /var/www/html/epesiBIM/epesi-1.1.3-rev7318/modules/Base/Mail/language/phpmailer.lang-zh_cn.php
	  0.0248    /var/www/html/phpadmin/shell2.php

	[[ Top 10 entropic files ]]
	  6.3978    /var/www/html/phpadmin/phpMyAdmin-3.3.8-all-languages/lang/chinese_simplified-utf-8.inc.php
	  6.0651    /var/www/html/epesiBIM/epesi-1.1.3-rev7318/modules/Base/Mail/language/phpmailer.lang-ch.php
	  6.0061    /var/www/html/webmedia/shell3.php
	  5.9870    /var/www/html/epesiBIM/epesi-1.1.3-rev7318/modules/Base/Mail/language/phpmailer.lang-zh.php
	  5.9797    /var/www/html/epesiBIM/epesi-1.1.3-rev7318/modules/Base/Mail/language/phpmailer.lang-zh_cn.php
	  5.9245    /var/www/html/phpadmin/shell2.php
	  5.8895    /var/www/html/wordpress/wordpress/wp-admin/js/revisions-js.php
	  5.8580    /var/www/html/phpadmin/phpMyAdmin-3.3.8-all-languages/lang/japanese-utf-8.inc.php
	  5.8400    /var/www/html/epesiBIM/epesi-1.1.3-rev7318/modules/Base/Mail/language/phpmailer.lang-ja.php
	  5.7602    /var/www/html/wordpress/wordpress/wp-admin/weevely.php

	[[ Top 10 longest word files ]]
	  111571    /var/www/html/webmedia/shell3.php
		2510    /var/www/html/webmedia/htdocs/templates/main.tpl.php
		1312    /var/www/html/joomla/shell.php
		 728    /var/www/html/wordpress/wordpress/wp-admin/js/revisions-js.php
		 536    /var/www/html/epesiBIM/epesi-1.1.3-rev7318/modules/Libs/QuickForm/3.2.11/HTML/QuickForm/Rule/Email.php
		 522    /var/www/html/wordpress/wordpress/wp-includes/functions.php
		 516    /var/www/html/phpadmin/phpMyAdmin-3.3.8-all-languages/libraries/tcpdf/tcpdf.php
		 516    /var/www/html/epesiBIM/epesi-1.1.3-rev7318/modules/Libs/PHPExcel/lib/PHPExcel/Shared/PDF/tcpdf.php
		 516    /var/www/html/epesiBIM/epesi-1.1.3-rev7318/modules/Libs/TCPDF/tcpdf4/tcpdf.php
		 516    /var/www/html/joomla/libraries/tcpdf/tcpdf.php

	[[ Highest Rank Files Based on test results ]]
		 83%    /var/www/html/webmedia/shell3.php
		 56%    /var/www/html/phpadmin/phpMyAdmin-3.3.8-all-languages/lang/chinese_simplified-utf-8.inc.php
		 43%    /var/www/html/wordpress/wordpress/wp-admin/js/revisions-js.php
		 36%    /var/www/html/epesiBIM/epesi-1.1.3-rev7318/modules/Base/Mail/language/phpmailer.lang-ch.php
		 26%    /var/www/html/webmedia/htdocs/templates/main.tpl.php
		 26%    /var/www/html/epesiBIM/epesi-1.1.3-rev7318/modules/Base/Mail/language/phpmailer.lang-zh.php
		 23%    /var/www/html/wordpress/wordpress/wp-admin/weevely.php
		 23%    /var/www/html/joomla/shell.php
		 20%    /var/www/html/joomla/templates/system/index.php
		 20%    /var/www/html/epesiBIM/epesi-1.1.3-rev7318/modules/Base/Mail/language/phpmailer.lang-zh_cn.php

We highly recommend that as a baseline, any file that is displayed in the Highest Rank Files list be investigated at a minimum.  We also recommend investigating any files that show up in any of the tests listed above, as some methods are more effective at detecting certain shells than others.  

##Windows
The tool is cross compatible with windows as well.    In the example below we use a regular expressing to just search for php and text files.

	python neopi.py -a c:\temp\phpbb "php|txt"

##Animal Shell
animal_shell_encoder.php and animal_shell_poc.php are two Proof-of-Concept-type examples scripts to implement an encoding that "should" evade many of the statistical tests NeoPI performs. They are poorly commented and the decoder large such that they are impractical.


