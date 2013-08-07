            <p><img class="avatar" src="{% if status.owner.avatar %}{{ status.owner.avatar.url }}.jpg{% else %}/static/img/avatar.png{% endif %}" /></p>      
            <p class="status"><a href="{% url mobile_user username=status.owner.user.username %}">{{ status.owner.user.username}}</a>: {{ status.render|safe }}</p>
            <p class="status-date">{{ status.date }}</p>
