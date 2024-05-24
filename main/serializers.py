from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
import datetime

class registerationserializer(serializers.Serializer):
    username=serializers.CharField()
    password=serializers.CharField()

    def validate(self, data):
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError('username exists')
        return data
    

    def create(self, validated_data):
        user=User.objects.create(username=validated_data['username'].lower())
        user.set_password(validated_data['password'])
        user.save()
        refresh=RefreshToken.for_user(user) # reason for generate token in register you can direct login in website by the token 
        AccessToken=str(refresh.access_token)
        # expires_in_timestamp = refresh.access_token.payload["exp"]
        # expires_in_datetime = datetime.fromtimestamp(expires_in_timestamp)
        # expires_in_seconds = int((expires_in_datetime - datetime.now()).total_seconds())
        return {
            "user":user,
            "refresh token":refresh,
            "Access token":AccessToken,
        }    
class loginserializer(serializers.Serializer):
    username=serializers.CharField()
    password=serializers.CharField()

    def validate(self, data):
        username=data.get('username')
        password=data.get('password')
        user=User.objects.filter(username=username).first()
        if not user:
            raise serializers.ValidationError("user not found")
        if not user.check_password(password):
            raise serializers.ValidationError("Incorrect password")
        refresh=RefreshToken.for_user(user)
        acces_token=str(refresh.access_token)
        print('----------------------------',refresh)
        # expires_in_timestamp = refresh.access_token.payload["exp"]
        # expires_in_datetime = datetime.fromtimestamp(expires_in_timestamp)
        # expires_in_seconds = int((expires_in_datetime - datetime.now()).total_seconds())
        return {
            "user": user.id,
            "access_token": acces_token,
            "refresh":str(refresh),
            # "expires_in": expires_in_seconds,
            # 'type':user.user_type
        }

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields="__all__"    
      
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['user','uuid','text']

    def create(self, validated_data):

        blog_uuid = self.context.get('blog_uuid')   
        blog_instance = Blog.objects.get(uuid=blog_uuid)
        validated_data['blog'] = blog_instance
        validated_data['user'] = self.context['request'].user
        return Comment.objects.create(**validated_data)

class BlogSerializer(serializers.ModelSerializer):
    blog_comments = CommentSerializer(many=True,required=False)
    total_comments = serializers.SerializerMethodField()
    total_likes = serializers.SerializerMethodField() # allow additonal info in serilizer 

    class Meta:
        model = Blog
        fields = ['uuid','title', 'content', 'main_image','total_likes','total_comments','blog_comments']
        read_only_fields = ['id']

    def get_total_comments(self, obj):
        return obj.blog_comments.count()
 
    def get_total_likes(self, obj):
        return Like.objects.filter(blog=obj, value=1).count()

