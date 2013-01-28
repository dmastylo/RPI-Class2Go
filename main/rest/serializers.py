from rest_framework import serializers
from c2g.models import *

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
    # a change
        model = Course

 
class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
    


class PSetSerializer(serializers.ModelSerializer):
    class Meta:
        model =  ProblemSet
    
    
class PSetExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model =  ProblemSetToExercise
    

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model =  Exercise
    

class ContentSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model =  ContentSection
    

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model =  Video
    

class VideoToExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model =  VideoToExercise

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model =  Exam

class ExamRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model =  ExamRecord

class ExamScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model =  ExamScore

class ExamScoreFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model =  ExamScore
