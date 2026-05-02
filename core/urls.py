from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('nova/', views.nova_movimentacao, name='nova'),
    

    # ✅ PDF por NF (único agora)
    path('pdf/nf/<str:nf>/', views.gerar_pdf_nf, name='pdf_nf'),

    # LOGIN
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # EDIÇÃO
    path('editar/<int:id>/', views.editar_movimentacao, name='editar'),
    path('excluir/nf/<str:nf>/', views.excluir_nf, name='excluir_nf'),
    path('item/excluir/<int:id>/', views.excluir_item, name='excluir_item')
]