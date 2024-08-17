from django.contrib import admin
from .models import Book, Category, Order, OrderItem

admin.site.register(Book)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(OrderItem)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publication_year', 'category', 'price', 'is_available')

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser