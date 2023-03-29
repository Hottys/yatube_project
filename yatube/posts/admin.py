from django.contrib import admin

from .models import Comment, Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'slug',
        'description'
    )
    list_editable = ('description', 'title', 'slug')
    search_fields = ('title',)
    empty_value_display = '-пусто-'


@admin.register(Comment)
class СommentsAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'author',
        'created'
    )
    list_filter = ('created',)
    empty_value_display = '-пусто-'
