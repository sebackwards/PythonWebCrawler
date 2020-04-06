# Simple web Crawler
This simple web crawler runs with Python3.

## Prerequisites

You will need _pipenv_. If you don't have it simply install on the project directory with:

```
python3 install pipenv
```

## Running the environment

Once the _pipenv_ environment is created you can start it on the project directory with:

```
pipenv shell
```

Next, install the project dependencies to setup the environment:

```
pipenv install
```

With all the dependencies installed you can crawl a website using _scrapper.py_ as:
```
pyhton3 scrapper.py <url> [options]:
  <url>		http(s)://somedomain.com
  -d		Refers to the number of times the script will run again over the URLs it finds in the HTML responses.
    		Example: a depth of 3 on root_domain.com will crawl the following responses:
    		Crawl root_domain [depth 1] -> Crawl responses [depth 2] ->  Crawl responses [depth 3]
    		(default 2)
  -o		Output filename
  -t		Number of threads
  -v		Validate found links (that weren't crawled) before saving: True/False
  --maxurls	Specifies maximum number of URLs to crawl (default 10000)
  --timeout	Specifies timeout for get request.(default 1s)
  --verify	Specifies SSL verification for https requests: True/False

```

NOTE: A large _maxurls_ can take time to complete. If you find yourself running the crawler for a large period of time and want to stop the execution you can do so by using the keyboard interrupt. The script will save the partial results to the output file.


**Example:** 
Run simple crawl on _http://domain.com_ until 500 urls are found and save to output.txt. 

```
python3 scrapper.py http://domain.com --maxurls 500 -o output.tx
```

**Example:**
Run crawl only on the index page of _http://domain.com_ with 5 threads.
```
python3 scrapper.py http://domain.com --maxurls 1 -o output.txt -t 5
```
**Example:**
Run crawl on _http://domain.com_ until 100 urls with SSL certificate verification.
```
python3 scrapper.py http://domain.com --maxurls 100 --verify True -o output.txt -t 5
```

## Running the test suite

The test suite is run with _pytest_. Results can be seen for the following tests:
* Bad _timeout_ input
* Bad _verify_ input
* Bad _thread_ input
* Bad _maxurls_ input
* Bad _url_ input

To run the test suit simply run _pytest_ from inside the environment:

```
pytest crawler_Test.py
```

## Author

* **Sebastian Toscano**
