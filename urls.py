from django.conf.urls.defaults import *
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^blip/', include('blip.foo.urls')),

    (r'^dashboard/?$', 'cockpit.views.main' ),
    (r'^user/(?P<username>\w+)/dashboard/?$', 'cockpit.views.main' ),
    (r'^user/(?P<username>\w+)/follow/?$', 'profile.views.follow' ),    
    (r'^status/(?P<object_id>\d+)/?$', 'cockpit.views.status'),
    (r'^status/?$', 'cockpit.views.status'),
    
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
                    
