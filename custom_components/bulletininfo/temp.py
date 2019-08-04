
import datetime
import urllib.request

URL_FORMAT = "https://www.uscis.gov/green-card/green-card-processes-and-procedures/visa-availability-priority-dates/when-file-your-adjustment-status-application-family-sponsored-or-employment-based-preference-visas-{0}-{1}"

currentdate = datetime.datetime.now()
currentMonth = currentdate.strftime("%B")
currentYear = currentdate.year
url = URL_FORMAT.format(currentMonth, currentYear)
print(url)
string_response = str(urllib.request.urlopen(url).read())
starting_index = string_response.find('<tr><th scope="col"><p>Employment- Based</p>')
print(starting_index)
if starting_index > 0:
    end_index = string_response.find('</tr>', starting_index + 5)
    string_result = string_response[starting_index:end_index]
    print(string_result)
    # p = re.compile(r'<.*?>')
    # tmp = p.sub('', string_result)
    # starting_index = string_response.find('<p>', end_index)
    # end_index = string_response.find('</p>', starting_index + 4)
    # p = re.compile(r'<.*?>')
    # string_result = string_response[starting_index:end_index]
    # tmp = p.sub('', string_result)
    
# else:
#     self._state = None