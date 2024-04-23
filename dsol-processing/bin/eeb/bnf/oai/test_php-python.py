#!/usr/local/bin/python2.6
import os
import time

done_file = '/opt/DSol/apache2/htdocs/eeb/bnf/oai/done.txt'
progress_file = '/opt/DSol/apache2/htdocs/eeb/bnf/oai/progress.txt'
progress_data = open(progress_file, 'w')
progress_data.close()

if os.path.isfile(done_file):
    os.remove(done_file)

for i in range(10):
    num = (i + 1) * 10
    progress_data = open(progress_file, 'w')
    progress_data.write(str(num))
    progress_data.close()
    time.sleep(3)

done = open(done_file, 'w')
done.write('done')
done.close()
