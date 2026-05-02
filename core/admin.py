from django.contrib import admin
from .models import Movimentacao, Item

class ItemInline(admin.TabularInline):
    model = Item
    extra = 1

@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    inlines = [ItemInline]