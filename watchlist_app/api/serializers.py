from rest_framework import serializers 
from watchlist_app.models import Watchlist,StreamPlatform,Review
 
class ReviewSerializer(serializers.ModelSerializer):
    review_user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Review
        exclude = ('watchlist',)
        # fields = "__all__"

class WatchlistSerializer(serializers.ModelSerializer):
    # reviews = ReviewSerializer(many=True,read_only=True)
    platform = serializers.CharField(source='platform.name')
    
    class Meta:
        model = Watchlist
        fields = "__all__"
        # fields = ['id','name','description']
        # exclude = ['name']
        

class StreamPlatformSerializer(serializers.ModelSerializer):
    watchlist = WatchlistSerializer(many=True,read_only=True)
    
    # watchlist = serializers.StringRelatedField(many=True)
    
    # watchlist = serializers.HyperlinkedRelatedField(
    #     many=True,
    #     read_only=True,
    #     view_name='movie-details'
    # )
    
    class Meta:
        model = StreamPlatform
        fields = "__all__"       
    
   
































# def name_length(value):
#     if len(value) < 2:
#         raise serializers.ValidationError("Name is too short!")


# class MovieSerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only= True)
#     name = serializers.CharField(validators=[name_length])
#     description = serializers.CharField()
#     active = serializers.BooleanField()
    
#     def create(self,validated_data):
#         return Movie.objects.create(**validated_data)
    
#     def update(self,instance,validated_data):
#         instance.name = validated_data.get('name',instance.name)
#         instance.description = validated_data.get('description',instance.description)
#         instance.active = validated_data.get('active',instance.active)
#         instance.save()
#         return instance
    
    
#     #object-level validation
#     def validate(self,data):
#         if data['name'] == data['description']:
#             raise serializers.ValidationError("Name and description should be different!")
#         else:
#             return data
    
    
#     # # Field-level validation - value contains name input value
#     # def validate_name(self,value):
#     #     if len(value) < 2:
#     #         raise serializers.ValidationError("Name is too short!")
#     #     else:
#     #         return value
        