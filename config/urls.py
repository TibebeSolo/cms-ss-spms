from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("students/", TemplateView.as_view(template_name="students_list.html"), name="students-list"),
    path("approvals/", TemplateView.as_view(template_name="approvals_queue.html"), name="approvals-queue"),
    path("login/", include("identity.urls")),
]
