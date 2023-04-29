"""diagram_chase_database URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include 
import database_app.views as db_views

from .views import (
    DefaultFormByFieldView,
    DefaultFormsetView,
    DefaultFormView,
    FormHorizontalView,
    FormInlineView,
    FormWithFilesView,
    HomePageView,
    MiscView,
    PaginationView,
    MessagesView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")), 
    path("", HomePageView.as_view(), name="home"),
    path("formset", DefaultFormsetView.as_view(), name="formset_default"),
    path("form", DefaultFormView.as_view(), name="form_default"),
    path("form_by_field", DefaultFormByFieldView.as_view(), name="form_by_field"),
    path("form_horizontal", FormHorizontalView.as_view(), name="form_horizontal"),
    path("form_inline", FormInlineView.as_view(), name="form_inline"),
    path("form_with_files", FormWithFilesView.as_view(), name="form_with_files"),
    path("pagination", PaginationView.as_view(), name="pagination"),
    path("misc", MiscView.as_view(), name="misc"),
    path("diagram_editor/<str:diagram_id>", db_views.diagram_editor, name="diagram_editor"),
    path("save_diagram/<str:diagram_id>", db_views.save_diagram_to_database, name="save_diagram"),
    path("load_diagram/<str:diagram_id>", db_views.load_diagram_from_database, name="load_diagram"),
    path("new_diagram", db_views.create_new_diagram, name="new_diagram"),
    path("messages", MessagesView.as_view(), name='messages'),
    path("my_diagram_list/<str:order_by>/<str:order_dir>/<int:page_num>", db_views.my_diagram_list, name='my_diagram_list'),
    path("embed_diagram/<str:diagram_id>", db_views.embed_diagram, name="embed_diagram"),
    path("functor_diagram/<str:diagram_id>", db_views.functor_diagram, name="functor_diagram"),
    path("rename_diagram/<str:diagram_id>", db_views.rename_diagram, name="rename_diagram"),
    path("reassign_category/<str:diagram_id>", db_views.reassign_category, name="reassign_category"),
]
