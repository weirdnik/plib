#

from django.conf.urls import url, include
#from django.contrib.auth.views import password_reset

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

import settings

import main.views
import cockpit.views
import profile.views
import blip.views

import django.views
import django.contrib.auth.views

urlpatterns = [

    url(r'^/?$', main.views.front, name='front_page'),    # front page
    url(r'^health/?', main.views.health),

    url(r'^dashboard/m/?$', cockpit.views.feed, dict(mobile=True), 'mobile_dashboard'),
    url(r'^dashboard/(?P<skip>\d+)/?$', cockpit.views.feed, dict(mobile=True), 'mobile_dashboard'),
    url(r'^dashboard/m/quote/(?P<quote>\d+)/?$', cockpit.views.feed, dict(mobile=True), 'mobile_dashboard'),
    url(r'^dashboard/m/reply/(?P<reply>\w+)/?$', cockpit.views.feed, dict(mobile=True, private=False), 'reply_dashboard'),
    url(r'^dashboard/m/private/(?P<reply>\w+)/?$', cockpit.views.feed, dict(mobile=True, private=True), 'private_dashboard'),
    url(r'^dashboard/m/message/(?P<slug>\w+)/?$', cockpit.views.feed, dict(mobile=True, private=True), 'message_dashboard'),

    url(r'^user/(?P<username>\w+)/mobile/?$', cockpit.views.feed, dict(mobile=True), 'mobile_user'),
    url(r'^user/(?P<username>\w+)/dashboard/?$', cockpit.views.main ),
    url(r'^user/(?P<username>\w+)/feed/?$', cockpit.views.feed ),
    url(r'^user/(?P<username>\w+)/follow/?$', profile.views.follow ),
    url(r'^user/(?P<username>\w+)/unfollow/?$', profile.views.unfollow ),
    url(r'^user/(?P<username>\w+)/blog/$', profile.views.blog ),
    url(r'^user/(?P<username>\w+)/blog/(?P<year>\d+)/(?P<week>\d+)/$', profile.views.blog, None, 'user_blog'),
    
    url(r'^status/(?P<object_id>\d+)/?$', cockpit.views.status),
    url(r'^status/?$', cockpit.views.status),
    url(r'^statusm/?$', cockpit.views.status, dict(mobile=True), 'mobile_status'),
    url(r'^status/(?P<object_id>\d+)/like/?$', cockpit.views.like, dict(mobile=True)),
    url(r'^status/(?P<object_id>\d+)/unlike/?$', cockpit.views.unlike, dict(mobile=True)),
    url(r'^status/(?P<object_id>\d+)/delete/?$', cockpit.views.delete, dict(mobile=True)),
    url(r'^status/(?P<object_id>\d+)/count/private/?$', cockpit.views.feed_count_since, dict(private=True), 'count_private'),
    url(r'^status/(?P<object_id>\d+)/count/?$', cockpit.views.feed_count_since, dict(private=False), 'count_public'),

    url(r'^tag/(?P<text>\w+)/$', cockpit.views.tag),
    url(r'^tag/(?P<text>\w+)/subscribe/?$', cockpit.views.tag_subscription,
      dict(action='subscribe'), 'tag_subscribe'),
    url(r'^tag/(?P<text>\w+)/unsubscribe/?$', cockpit.views.tag_subscription,
      dict(action='unsubscribe'), 'tag_unsubscribe'),
    url(r'^tag/(?P<text>\w+)/ignore/?$', cockpit.views.tag_subscription,
      dict(action='ignore'), 'tag_ignore'),
    url(r'^tag/(?P<text>\w+)/unignore/?$', cockpit.views.tag_subscription,
      dict(action='unignore'), 'tag_unignore'),
      
    # user management stuff
    url(r'^account/login/$', django.contrib.auth.views.login,
      {'template_name': 'login.html'}, 'login_user'), #fixme
    url(r'^account/logout/$', django.contrib.auth.views.logout,
      {'template_name': 'logout.html', 'next_page': '/'}, 'logout_user'),
    url(r'^account/register/$', profile.views.register, None, 'create_user'),
    url(r'^account/$', profile.views.edit, None, 'edit_account'),
    url(r'^account/confirm/(?P<slug>\w+)/?$', profile.views.confirm),
    url(r'^account/import/?$', blip.views.importer, {}, 'import_blip'),

    # password handling
    url(r'^account/reset/?$', django.contrib.auth.views.password_reset,
      {'post_reset_redirect' : '/account/reset/sent/',
        'from_email': 'Plum.ME <blip@plum.me>'
        }, 'reset_password'),
    url(r'^account/reset/sent/?$', django.contrib.auth.views.password_reset_done,
      {'template_name': 'registration/password_reset_notice.html'}, ), #change template
    url(r'^account/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/?$',
      django.contrib.auth.views.password_reset_confirm,
      {'post_reset_redirect' : '/account/reset/done/'}, 'password_reset_confirm'),
    url(r'^account/reset/done/$', django.contrib.auth.views.password_reset_complete),

    
    # legacy paths, hardcoded somewhere
    url(r'^accounts/login/$', django.contrib.auth.views.login,
      {'template_name': 'login.html'}),
    url(r'^accounts/logout/$', django.contrib.auth.views.logout,
      {'template_name': 'logout.html'}),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
]

# if settings.DEBUG:
#     urlpatterns.append(
#         url(r'^static/(?P<path>.*)$', django.views.static.serve,
#             {'document_root': settings.MEDIA_ROOT}),
#     )
                    
