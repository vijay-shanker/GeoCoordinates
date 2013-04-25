Using Geocoordinate
--------------------
Django-Geocoordinate provide a way to make calls to Google Maps API Web Services
as defined here https://developers.google.com/maps/documentation/webservices/

It can be used to find latitude, longitude for any place, find  geographic distance bewtween the coordinates,
elevation of given coordinates from sea-level in meters, a list of all geographic coordinates from the object at which this method is called upon
within a given radius from database.

1. Put Geocoordinate in you installed apps in settings.py, and run syncdb.
2. Create a OneToOneField in model where you want to store coordinates and have that model inherit AddGeoEncoder instead of models.Model
   e.g:
   class Place(AddGeoEncoder):
       name = models.CharField(max_length=50)
       address = models.CharField(max_length=50)
       coordinates = models.OneToOneField(GeoCoordinate,null=True,blank=True) 
       def __str__(self):
           return self.name
3. To find the geocoordinates of any such place, you can do pass the name of field which stores your geocoordinates (coordinates in above example), 
   and fieldname which constitutes the address for this place as tuple
   e.g: placeobject.geo_encode('coordinates',('name','address'))

4. class AddGeoEncoder:
    abstract base class for every model where a geographhic coordinate field is attached , should inherit.
    this provide the model with a geo_encode() method, which takes the name of coordinate_field (as defined in model)
    and a tuple of fieldnames which defines address (address_line1, state, zip) for the model, to query google map api
    to populate coordinate field of your model.

5. def geo_encode(self,coordinate_field,address_field):
    its a method of AddGeoEncoder class which uses google's map api services to
    query and recieve response and update the coordinate fieldname passed to it.
    it takes three arguments: 
       self, instance which its called upon by
       coordinate_field, fieldname which holds OneToOne/Foreign_key relation
       address_fields, fieldnames which describe the address to be geocoded as tuple 
       it updates the coordinate_field with a value or raises       
       NameError which is status of call in case of failure/zero results
 
      

