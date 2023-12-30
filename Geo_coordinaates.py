import geocoder as geo
def get_coordinates():
    return geo.ip("me").latlng
coordinates= get_coordinates()
print("Your current coordinates are:", coordinates)