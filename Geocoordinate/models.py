from django.db import models
from math import acos, cos, sin
import urllib2
import json
from django.db import connection
 
class AddGeoEncoder(models.Model):
    '''
    abstract base class for every model where a geographhic coordinate field is attached , should inherit.
    this provide the model with a geo_encode() method, which takes the name of coordinate_field (as defined in model)
    and a tuple of fieldnames which defines address (address_line1, state, zip) for the model, to query google map api
    to populate coordinate field of your model. 
    '''
    class Meta:
        abstract = True
    def geo_encode(self,coordinate_field,address_field):
        '''
        its a method of AddGeoEncoder class which uses google's map api services to
        query and recieve response and update the coordinate fieldname passed to it.
        it takes three arguments:
        self, instance which its called upon by
        coordinate_field, fieldname which holds OneToOne/Foreign_key relation
        address_fields, fieldnames which describe the address to be geocoded as tuple
        it updates the coordinate_field with a value or raises NameError which is status
        of call in case of failure/zero results 
        '''
        address_string = ' '.join([self.__dict__[each] for each in address_field])
        address_string = address_string.replace(' ','+')
        url_string = 'http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=true'%(address_string)
        url = urllib2.urlopen(url_string)
        json_obj = json.loads(url.read())
        if json_obj['status'] == 'OK':
            latitude = json_obj['results'][0]['geometry']['location']['lat']
            longitude = json_obj['results'][0]['geometry']['location']['lng']
            geocoord_obj = GeoCoordinate.objects.create(latitude=latitude,longitude=longitude)
            self.__dict__[coordinate_field] = geocoord_obj
            self.__dict__[coordinate_field+'_id'] = geocoord_obj.id
            self.save()            
        else:
            raise NameError(json_obj['status'] )


class GeoCoordinate(models.Model):
    latitude = models.FloatField(null=True,blank=True)
    longitude = models.FloatField(null=True,blank=True)
    
    def geographic_distance(self,geocord_obj):
        '''
        calculates the geographic distance bewtween the coordinate of self and one that is passed.
        '''
        return acos(sin(geocord_obj.latitude)*sin(self.latitude) + \
            cos(geocord_obj.latitude)*cos(self.latitude)*cos(self.longitude -(geocord_obj.longitude)))*6371
    
    def elevations(self):
        '''
        calculates the elevation of given coordinates from sea-level in meters.
        '''
        response = urllib2.urlopen('http://maps.googleapis.com/maps/api/elevation/json?locations='\
                                   +str(self.latitude)+','+str(self.longitude)+'&sensor=true')
        response_obj = json.loads(response.read())
        return obj['results'][0]['elevation']
    
    def in_vicinity(self,radius):
        '''
        returns a list of all geographic coordinates from the object at which this method is called upon
        within a given radius from database.
        '''
        cursor = connection.cursor()
        cursor.execute('SELECT id from GeoCoordinate_geocoordinate WHERE acos(sin(%f) * sin(latitude) +\
        cos(%f) * cos(latitude) * cos(longitude - (%f))) * 6371 <= %d;'%(self.latitude,self.latitude,self.longitude,radius))
        tupled = cursor.fetchall()
        return [each[0] for each in tupled]    
    
    def __str__(self):
        return '%f,%f'%(self.latitude,self.longitude)
    

    