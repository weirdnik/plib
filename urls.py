from django.conf.urls.defaults import *
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^blip/', include('blip.foo.urls')),

    (r'^/?$', 'main.views.front' ),    # front page
    
    (r'^dashboard/?$', 'cockpit.views.main' ),
    (r'^dashboard/m/?$', 'cockpit.views.feed', dict(mobile=True), 'mobile_dashboard'),
    
    (r'^user/(?P<username>\w+)/dashboard/?$', 'cockpit.views.main' ),
    (r'^user/(?P<username>\w+)/feed/?$', 'cockpit.views.feed' ),    
    (r'^user/(?P<username>\w+)/follow/?$', 'profile.views.follow' ),    
    (r'^user/(?P<username>\w+)/unfollow/?$', 'profile.views.unfollow' ),    
    (r'^user/(?P<username>\w+)/blog/?$', 'profile.views.blog' ),    
    (r'^status/(?P<object_id>\d+)/?$', 'cockpit.views.status'),
    (r'^status/?$', 'cockpit.views.status'),
    
    (r'^statusm/?$', 'cockpit.views.status', dict(mobile=True), 'mobile_status'),    


    (r'^tag/(?P<tag>\w+)/$', 'cockpit.views.tag'),
    
    (r'^account/login/$', 'django.contrib.auth.views.login',
      {'template_name': 'login.html'}),
    (r'^account/logout/$', 'django.contrib.auth.views.logout',
      {'template_name': 'logout.html'}),

    (r'^account/register/$', 'profile.views.register'),
    (r'^account/$', 'profile.views.edit'),    
    (r'^account/confirm/(?P<slug>\w+)/?$', 'profile.views.confirm'),    
    # Uncomment the admin/doc line below to enable admin documentation:
    #(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', 
            {'document_root': settings.MEDIA_ROOT}),
    )
                    
