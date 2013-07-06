        <p><img class="avatar" src="{% if status.owner.avatar %}{{ status.owner.avatar.url }}.jpg{% else %}/static/img/avatar.png{% endif %}" /></p>      
        <p class="status">{{ status.owner.user.username}}: {{ status.render|safe }}</p>
        <p class="status-date">{{ status.date }}</p>
