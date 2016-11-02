#

from django.conf.urls.defaults import *
#from django.contrib.auth.views import password_reset

import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^blip/', include('blip.foo.urls')),

    (r'^/?$', 'main.views.front', None, 'front_page'),    # front page
    (r'^health/?', 'main.views.health'),
        
    (r'^dashboard/m/?$', 'cockpit.views.feed', dict(mobile=True), 'mobile_dashboard'),
    (r'^dashboard/(?P<skip>\d+)/?$', 'cockpit.views.feed', dict(mobile=True), 'mobile_dashboard'),
    (r'^dashboard/m/quote/(?P<quote>\d+)/?$', 'cockpit.views.feed', dict(mobile=True), 'mobile_dashboard'),
    (r'^dashboard/m/reply/(?P<reply>\w+)/?$', 'cockpit.views.feed', dict(mobile=True, private=False), 'reply_dashboard'),
    (r'^dashboard/m/private/(?P<reply>\w+)/?$', 'cockpit.views.feed', dict(mobile=True, private=True), 'private_dashboard'),
    (r'^dashboard/m/message/(?P<slug>\w+)/?$', 'cockpit.views.feed', dict(mobile=True, private=True), 'message_dashboard'),

    (r'^user/(?P<username>\w+)/mobile/?$', 'cockpit.views.feed', dict(mobile=True), 'mobile_user'),  
    (r'^user/(?P<username>\w+)/dashboard/?$', 'cockpit.views.main' ),
    (r'^user/(?P<username>\w+)/feed/?$', 'cockpit.views.feed' ),    
    (r'^user/(?P<username>\w+)/follow/?$', 'profile.views.follow' ),    
    (r'^user/(?P<username>\w+)/unfollow/?$', 'profile.views.unfollow' ),    
    (r'^user/(?P<username>\w+)/blog/$', 'profile.views.blog' ),    
    (r'^user/(?P<username>\w+)/blog/(?P<year>\d+)/(?P<week>\d+)/$', 'profile.views.blog', None, 'user_blog'),
    
    (r'^status/(?P<object_id>\d+)/?$', 'cockpit.views.status'),
    (r'^status/?$', 'cockpit.views.status'),  
    (r'^statusm/?$', 'cockpit.views.status', dict(mobile=True), 'mobile_status'),    
    (r'^status/(?P<object_id>\d+)/like/?$', 'cockpit.views.like', dict(mobile=True)),    
    (r'^status/(?P<object_id>\d+)/unlike/?$', 'cockpit.views.unlike', dict(mobile=True)),        
    (r'^status/(?P<object_id>\d+)/delete/?$', 'cockpit.views.delete', dict(mobile=True)),        
    (r'^status/(?P<object_id>\d+)/count/private/?$', 'cockpit.views.feed_count_since', dict(private=True), 'count_private'),            
    (r'^status/(?P<object_id>\d+)/count/?$', 'cockpit.views.feed_count_since', dict(private=False), 'count_public'),            

    (r'^tag/(?P<text>\w+)/$', 'cockpit.views.tag'),
    (r'^tag/(?P<text>\w+)/subscribe/?$', 'cockpit.views.tag_subscription',
      dict(action='subscribe'), 'tag_subscribe'),
    (r'^tag/(?P<text>\w+)/unsubscribe/?$', 'cockpit.views.tag_subscription',
      dict(action='unsubscribe'), 'tag_unsubscribe'),
    (r'^tag/(?P<text>\w+)/ignore/?$', 'cockpit.views.tag_subscription',
      dict(action='ignore'), 'tag_ignore'),
    (r'^tag/(?P<text>\w+)/unignore/?$', 'cockpit.views.tag_subscription',
      dict(action='unignore'), 'tag_unignore'),
      
    # user management stuff
    (r'^account/login/$', 'django.contrib.auth.views.login',
      {'template_name': 'login.html'}, 'login_user'), #fixme
    (r'^account/logout/$', 'django.contrib.auth.views.logout',
      {'template_name': 'logout.html', 'next_page': '/'}, 'logout_user'),
    (r'^account/register/$', 'profile.views.register', None, 'create_user'),
    (r'^account/$', 'profile.views.edit', None, 'edit_account'),    
    (r'^account/confirm/(?P<slug>\w+)/?$', 'profile.views.confirm'),        
    (r'^account/import/?$', 'blip.views.importer', {}, 'import_blip'),        

    # password handling
    (r'^account/reset/?$', 'django.contrib.auth.views.password_reset',
      {'post_reset_redirect' : '/account/reset/sent/',
        'from_email': 'Plum.ME <blip@hell.pl>'
        }, 'reset_password'),            
    (r'^account/reset/sent/?$', 'django.contrib.auth.views.password_reset_done',
      {'template_name': 'registration/password_reset_notice.html'}, ), #change template
    (r'^account/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/?$', 
      'django.contrib.auth.views.password_reset_confirm', 
      {'post_reset_redirect' : '/account/reset/done/'}, 'password_reset_confirm'),
    (r'^account/reset/done/$', 'django.contrib.auth.views.password_reset_complete'),      

    
    # legacy paths, hardcoded somewhere
    (r'^accounts/login/$', 'django.contrib.auth.views.login',
      {'template_name': 'login.html'}),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout',
      {'template_name': 'logout.html'}),

    # Uncomment the admin/doc line below to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', 
            {'document_root': settings.MEDIA_ROOT}),
    )
                    
