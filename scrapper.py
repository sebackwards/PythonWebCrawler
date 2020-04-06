
#!/usr/bin/python3
# Version 1.1
import getopt
import re
import requests
import sys
import time
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing.dummy import threading
from html.parser import HTMLParser

class HTMLParse(HTMLParser):
    from_url = None
    def handle_starttag(self, tag, attrs):
        global URL_todo
        #Handle HTML attributes (This goes beyond looking just at tags for href,
        #link,source, etc. since in practice, hyperlinks can use any kind of tag and attribute)
        for _,value in attrs:
            if(value):
                for data in value.split(' '):
                    url=find_URL(data,self.from_url)
                    if(url and url not in URL_todo and url not in URL_crawled):
                        #I might need synchronization here
                        print(f'Found URL: \033[4m{url}\033[0m')
                        URL_todo.add(url)

#Globals Options
filename = 'crawled.txt'
threads = 6
timeout_req = 1
verify_ssl = True
max_crawled = 10000
depth = 2
validate = False
run_spinner = True
domain=''
URL_todo = set()
URL_crawled = set()
requests.packages.urllib3.disable_warnings() #Disable SSL warning when cert verification is off

#Parse data from HTML response to determine if any URLs are present
def find_URL(data,from_url):
    global domain
    url = None #Local url

    # TODO: Maybe use specific tags to search in: href. div, src, etc to reduce false positives.
    pattern=r'(.*' + domain + r'.*)|(\.\.*\/.*)|(\.\/.*)|(^\/.*)|(^\w+\.[A-Za-z]+$)'
    matched=re.match(pattern,data)

    #If URL pattern was found, proceeds to be cleaned before validating
    if(matched):
        #Extract URL from match
        url=matched.group()

        #Clean url (e.g add domain to non-absolute paths)
        if('http' not in url and 'www' not in url):
            if (url[0]!='/'): # file.php ./file2.php
                if(url[0:1]=='./' and url[2:] not in from_url):
                    url = (f'{from_url}/{url}')
            else:
                url = (f'http://{domain}{url}')

        #Filter URLs to crawl only with those inside the subdomain in scope
        dom = extract_domain(url)
        if (dom and (domain in dom)):
            return url
    return None

def extract_domain(url):
    pattern=r"^[a-z][a-z0-9+\-.]*:\/\/([a-z0-9\-._~%!$&'()*+,;=]+@)?([a-z0-9\-._~%]+|\[[a-z0-9\-._~%!$&'()*+,;=:]+\])"
    dom=re.match(pattern,url)
    if(dom):
        return dom.group(2)
    else:
        return None

def request_url(url):
    global URL_crawled #Added for good practices
    global timeout_req
    global verify_ssl
    try:
        #Filter those URLs already verified
        if(url not in URL_crawled):
            response = requests.get(url,timeout=timeout_req,verify=verify_ssl)
        if(response.status_code != 404):
            return response
        return -1

    except requests.exceptions.Timeout:
        print(f'Could not fetch url: \033[4m{url}\033[0m. Timeout error. Try re-running with --timeout flag')
        return -1

    except requests.exceptions.SSLError as err:
        print(f'Could not fetch url: \033[4m{url}\033[0m. SSL verification error. Try re-running with --verify True/False flag')
        return -1

    except Exception:
        error=f'Could not fetch url: \033[4m{url}\033[0m.'
        print(error)
        return -1

def build_URL_list(url):
    global URL_crawled
    global max_crawled

    if(len(URL_crawled) >= max_crawled):
        return
    if(url not in URL_crawled):
        response = request_url(url)
        if(response != -1):
            #Parse response
            if('text/html' in response.headers['Content-Type']):
                parser=HTMLParse()
                parser.from_url = url
                parser.feed(response.text)
        URL_crawled.add(url) #Potentially I need synchronization here

def validate_todo():
    global run_spinner
    global URL_todo
    global threads
    URLs_valid = set()

    print('Validating URLs ', end='')
    #Spinner thread
    sp = threading.Thread(target=spinner_print)
    sp.start()

    #URL threads
    pool = ThreadPool(threads)
    responses = pool.map(request_url, URL_todo)

    #Close pools
    pool.close()
    pool.join()
    run_spinner = False
    sp.join()
    print('Done')
    for url,response in zip(URL_todo,responses):
        if(response != -1):
            URLs_valid.add(url)
    return(URLs_valid)

def usage():
    print(f'Usage:\npyhton3 {sys.argv[0]} <url> [options]:\n'
    '  <url>\t\thttp(s)://somedomain.com\n'
    '  -d\t\tRefers to the number of times the script will run again over the URLs it finds in the HTML responses.\n'
    '    \t\tExample: a depth of 3 on root_domain.com will crawl the following responses:\n'
    '    \t\tCrawl root_domain [depth 1] -> Crawl responses [depth 2] ->  Crawl responses [depth 3]\n'
    '    \t\t(default 2)\n'
    '  -o\t\tOutput filename\n'
    '  -t\t\tNumber of threads\n'
    '  -v\t\tValidate found links (that weren\'t crawled) before saving: True/False\n'
    '  --maxurls\tSpecifies maximum number of URLs to crawl (default 10000)\n'
    '  --timeout\tSpecifies timeout for get request.(default 1s)\n'
    '  --verify\tSpecifies SSL verification for https requests: True/False')

def map_site(URLs_set):
    URLs_sorted = sorted(URLs_set)
    sep='-'
    level = 1
    sitemap=list()
    sitemap.append('-> ' +f'{URLs_sorted[0]}')
    for i,_ in enumerate(URLs_sorted):
        if(i+1 < len(URLs_sorted)):
            root = URLs_sorted[i].split('://')[1:][0].split('/')
            test = URLs_sorted[i+1].split('://')[1:][0].split('/')
            level=1
            for dir_root,dir_test in zip(root,test):
                if(dir_root==dir_test):
                    level+= 2
            sitemap.append(str(sep*level) + '> ' + ''*level + f'{URLs_sorted[i+1]}')
    save(sitemap)

def save(URLs_set):
    global filename
    global URL_todo
    global URL_crawled
    #Sitemap
    sitemap_name = filename.split('.')[0]+'-sitemap.txt'
    heads = f'Sitemap of {domain}\n'
    seps = '-'*len(heads)
    print(f'Saving sitemap to {sitemap_name}...')
    with open(sitemap_name,'w') as f:
        f.write(f'{heads}{seps}\n')
        for url in (URLs_set):
            f.write(url+'\n')

    #Results
    headc = 'URLs Found and Crawled:\n'
    sepc = len(headc)*'-'
    headf = '\nURLs Found but not validated:\n'
    sepf = len(headf)*'-'
    print(f'Saving crawl results to {filename}...')
    with open(filename,'w') as f:
        f.write(f'{headc}{sepc}\n')
        for url in (sorted(URL_crawled)):
            f.write(url+'\n')
        f.write(f'{headf}{sepf}\n')
        for url in (sorted(URL_todo)):
            f.write(url+'\n')

    print(f'Crawled:{len(URL_crawled)}')
    print(f'Discovered: {len(URL_crawled.union(URL_todo))}')
    print('Exiting...')

def spinner_print():
    global run_spinner
    counter = 0

    while run_spinner:
        time.sleep(0.75)
        sys.stdout.write('.')
        sys.stdout.flush()
        counter += 1
        if(counter == 4):
            counter = 0
            sys.stdout.write('\b'*4)
            sys.stdout.flush()
            sys.stdout.write(' '*4)
            sys.stdout.write('\b'*4)
            sys.stdout.flush()

def set_options(opts,args):
    bools ={'False':False,
            'True':True}
    for opt,arg in zip(opts,args):
        try:
            if(opt[0] == '-o'):
                global filename
                filename = str(arg)
            if(opt[0] == '-t'):
                global threads
                threads = int(arg)
            if(opt[0] == '-d'):
                global depth
                depth = int(arg)
            if(opt[0] == '-v'):
                global validate
                validate = bools[arg]
            if(opt[0] == '--timeout'):
                global timeout_req
                timeout_req = int(arg)
            if(opt[0] == '--maxurls'):
                global max_crawled
                max_crawled = int(arg)
            if(opt[0] == '--verify'):
                global verify_ssl
                verify_ssl = bools[arg]
        except Exception as err:
            print(f'Cannot set argument {opt[0]}. Invalid type, check arguments and try again.')
            usage()
            raise TypeError

def main(argv):
    #Verify minimum arguments
    if(len(argv)<2):
        usage()
        return -1

    try:
        opt = 'dotv'
        long_opt = ['maxurls','timeout','verify']
        opts,args = getopt.gnu_getopt(argv[2:],opt,long_opt)
        set_options(opts,args)
    except getopt.GetoptError:
        usage()
        return -1
    except Exception as err: #Added error message for any other errors
        print(err)
        return -1

    #Validate root_url
    root_url=argv[1]
    response = request_url(root_url)
    if(response == -1):
        print('Verify the domain and try again')
        usage()
        return -1

    # Extract domain from input
    global domain
    domain = extract_domain(root_url)
    #Vars
    global URL_todo
    global URL_crawled
    global threads
    global max_crawled
    global depth
    global validate
    iteration = 1
    #Add root_url to worksheet
    URL_todo.add(root_url)
    while(URL_todo != set() and len(URL_crawled) < max_crawled and iteration <= depth):

        # Create pool of workers.
        # Note: async seems to have a bit of an issue with the requests module because
        # apparently requests is not designed to notify the event loop that it’s blocked.
        # Threads seemed like a better solution since my botleneck was in I/O from the network.
        # Multiprocessing wasn't going to work either because the problem is not CPU bounded
        pool = ThreadPool(threads)
        #Map threads to URL list
        pool.map(build_URL_list, URL_todo)
        #Close pools
        pool.close()
        pool.join()

        #If maxcrawl is large enough, run until there's nothing left to do
        URL_todo = URL_todo.difference(URL_crawled)
        iteration+=1

        if(len(URL_crawled) >= max_crawled):
            print('\nDone: Max urls crawled. If you want to re-run with a bigger target use --maxurls flag')
        if(iteration > depth):
            print('\nDone: Max depth reached. If you want to re-run with a bigger target use -d flag')

    if(validate):
        print('Validate flag detected. Starting validation on URLs found before saving ')
        URL_todo = validate_todo()
    map_site(URL_crawled.union(URL_todo))

if __name__ == "__main__":
    try:
        argv=sys.argv
        main(argv)
    except (KeyboardInterrupt):
        print('Keyboard interrupt detected... Stopping')
        run_spinner = False
        map_site(sorted(URL_crawled.union(URL_todo)))
        SystemExit
    except Exception as err:
        print(err)