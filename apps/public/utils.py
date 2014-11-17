import time
from datetime import datetime
from subprocess import call


def show_in_browser(response):
    """
    Write the response content into a temporary HTML file and
    open it into your default browser.

    > client = Client()
    > response = client.get('/some/page/')
    > show_in_browser(response)

    """
    file_path = '/tmp/django_test_show_in_browser_%s.html' % datetime.now().strftime('%Y%m%d%H%M%S')
    f = open(file_path, 'w')
    f.write('%s\n' % response.content)
    call(["open", file_path])
    time.sleep(5)
    call(["rm", file_path])
