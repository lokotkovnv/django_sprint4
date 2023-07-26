from django.contrib import admin

from blog.models import Category, Location, Post


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
    )
    list_editable = (
        'is_published',
        'text',
        'pub_date',
        'category',
    )
    search_fields = (
        'title',
        'text',
        'category',
    )
    list_filter = (
        'category',
    )
    list_display_links = (
        'title',
    )


admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Post, PostAdmin)
