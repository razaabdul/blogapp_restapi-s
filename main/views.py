from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import NotFound
from rest_framework.decorators import permission_classes,action
from datetime import datetime
from django.utils import timezone

from .models import *

# Create your views here.                   
class UsersView(viewsets.ModelViewSet):  
    @action(detail=False,methods=['POST'],url_path="register")
    def register(self,request): 
        try:    
            data=request.data
            serializer=registerationserializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({"msg":"account is created successfully"},status=status.HTTP_200_OK)
            return Response({"data":{},"msg":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"data":{},"msg":"something went wrong"},status=status.HTTP_400_BAD_REQUEST)    

    @action(detail=False,methods=['POST'],url_path="login")    
    def login(self,request):
        try:
            data=request.data
            serializer=loginserializer(data=data)
            print(serializer)
            if not serializer.is_valid():
                return Response({
                    "data":serializer.errors,
                    "msg":"something went wrong"
                },status=status.HTTP_400_BAD_REQUEST)
            Response_data=serializer.validated_data
            print(Response_data)
            return Response(Response_data,200)       
        except Exception as e:
            return Response(
                str(e),
                status=status.HTTP_400_BAD_REQUEST,
            )
   
class blogview(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    def post(self,request):
        try:
            user=request.user
            serializer = BlogSerializer(data=request.data)
            
            if serializer.is_valid():
                serializer.save(user=user)
                return Response({"message": "Success"}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def get(self, request,pk=None):
        try:
            if pk: 
                blog_obj=Blog.objects.get(uuid=pk)
    
                comments = Comment.objects.filter(blog=blog_obj)
                serializer = BlogSerializer(blog_obj, context={"comments":comments})
                return Response(serializer.data )
            else: 
                blog_obj = Blog.objects.all()
                blg = Blog.objects.filter(user=request.user).count()# show the total blogs of every user
                print(blg)
        
                serializer = BlogSerializer(blog_obj, many=True)
                return Response(serializer.data)
        except Blog.DoesNotExist:
            raise NotFound("Blog post not found")
    def put(self,request,pk):
        try:
            instance = Blog.objects.get(uuid=pk)
        except Blog.DoesNotExist:
            return Response({"error": "Object not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user != instance.user:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = BlogSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class commentview(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    def post(self, request, blog_uuid):
        try:
            serializer = CommentSerializer(data=request.data, context={'blog_uuid': blog_uuid,"request":request})
            print(serializer)
            if serializer.is_valid():
                serializer.save()   
                return Response({"message": "Success"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def put(self,request,blog_uuid):
        try:
            instance =Comment.objects.get(uuid=blog_uuid)
        except Exception as e:
            return Response(str(e))
        if request.user != instance.user:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        serializer = CommentSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg":"comment updated successfully"},200)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, blog_uuid):
        try:
            comment = Comment.objects.get(uuid=blog_uuid)
            
            # Check if the authenticated user is the author of the comment
            if request.user == comment.user:
                comment.delete()
                return Response({"message": "Comment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            else:
                raise ("You do not have permission to delete this comment.")
        
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "Sorry this comment is not posted by you !"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class likeview(APIView):    
    permission_classes = [IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    def post(self,request,pk=None):
        blog=Blog.objects.get(uuid=pk)
        user=request.user
        try:               
            like=Like.objects.get(user=user,blog=blog)
            if like.value == 1:
                like.value = 0
            else:
                like.value = 1  
            like.save()        
        except Like.DoesNotExist:
            like=Like.objects.create(user=user,blog=blog,value=1)
        like_count = Like.objects.filter(blog=blog, value=1).count()
        return Response({"like":like.value,"like_count":like_count},status=status.HTTP_200_OK)     
    
class FilterBlogsByMonth(APIView):
     def get(self, request, month_name):
        try:
            # month_name = request.query_params.get('month_name', None)
            # if month_name is None:
            #     return Response({"error": "Month name is required"}, status=400)
            month_name_lower = month_name.lower()

            month_number = timezone.datetime.strptime(month_name_lower, '%B').month
            start_date = timezone.datetime(year=timezone.now().year, month=month_number, day=1)
            end_date = start_date.replace(day=28) + timezone.timedelta(days=4)

            filtered_blogs = Blog.objects.filter(created_at__gte=start_date, created_at__lt=end_date)
            if not filtered_blogs:
                return Response("dont have data in this month !")
            serializer = BlogSerializer(filtered_blogs, many=True)
            return Response(serializer.data)
        except ValueError:
            return Response({"error": "Invalid month name provided"}, status=400)



class userprofile(APIView):
    def get(self,request):
        data=request.user
        obj=Blog.objects.filter(user=uuid)
        print(obj.count())
        return Response()

