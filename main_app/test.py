import requests

url = "https://booking-com.p.rapidapi.com/v1/hotels/reviews"

querystring = {
    "hotel_id":"2903239",
    "locale":"en-gb",
    "sort_type":"SORT_MOST_RELEVANT",
    "customer_type":"solo_traveller,review_category_group_of_friends",
    "language_filter":"en-gb,de,fr"}

headers = {
	"X-RapidAPI-Key": "e15e09ce4fmsh991f91f0cf96a05p115e8fjsn91e3af6919fc",
	"X-RapidAPI-Host": "booking-com.p.rapidapi.com"
}

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)


