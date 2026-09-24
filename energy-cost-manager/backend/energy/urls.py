from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
router=DefaultRouter(); router.register("uploads",UsageUploadViewSet,basename="uploads"); router.register("providers",ProviderViewSet,basename="providers"); router.register("plans",PlanViewSet,basename="plans")
urlpatterns=[path("health/",health),path("",include(router.urls)),path("compare/",compare),path("comparisons/",ComparisonListView.as_view()),path("comparisons/<uuid:pk>/",ComparisonDetailView.as_view()),path("comparisons/<uuid:pk>/report.csv",comparison_report)]
