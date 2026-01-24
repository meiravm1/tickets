import requests
def main():
    #make a request
    consumer_key = 'VQfSVciGUlwU230o4q9SgMAyyrg6EBoy'
    response = requests.get(f"https://app.ticketmaster.com/discovery/v2/events.json?apikey={consumer_key}")
    print(response.text)
if __name__ == '__main__':
    main()