{% if status.action %}
      <div class="status-info">
          <p>(i) {{ status.render|safe }}</p>
      </div>
      {% else %}
      <div class="{% if status.private %}private {% endif %}status">
          <img class="avatar"
               src="{% if status.owner.avatar %}{{ status.owner.avatar.url }}{% else %}/static/img/avatar.png{% endif %}"/>

          <p class="status"><span title="{{ status.date }}">[&#x231A;]</span>
              <strong><a href="{% url mobile_user username=status.owner.user.username %}">{{ status.owner.user.username }}</a></strong>{% if not status.recipient %}:{% endif %}
              {{ status.render|safe }}</p>

          <div class="status-meta">{% if not status.recipient %}
              [&hearts; {{ status.num_likes.distinct.count|safe }} ]{% endif %}
              <a href="{% url cockpit.views.status object_id=status.id %}">link</a>
              <a href="{% url mobile_dashboard quote=status.id %}">cytuj</a>{% if not user.username = status.owner.user.username %} <a href="{% if status.private %}{% url private_dashboard reply=status.owner.user.username %}{% else %}{% url reply_dashboard reply=status.owner.user.username %}{% endif %}">odpowiedz</a>{% endif %}

              {% if status.private or status.recipient or user.username == status.owner.user.username %}
              <form method="POST" action="{% url cockpit.views.delete object_id=status.id %}">
                  {% csrf_token %}
                  <div><input type="submit" value="usun" class="btn btn-small btn-link"/></div>
              </form>
              {% else %}
              <div class="likebox">
                  {% if user.username in status.liking %}
                  <form method="POST" action="{% url cockpit.views.unlike object_id=status.id %}">
                      {% csrf_token %}
                      <div><input type="submit" value="nie lub" class="btn btn-small btn-link"/></div>
                  </form>
                  {% else %}
                  <form method="post" action="{% url cockpit.views.like object_id=status.id %}">
                      {% csrf_token %}
                      <div><input type="submit" value="polub" class="btn btn-small btn-link"/></div>
                  </form>
                  {% endif %}
              </div>
              <!-- end status-likebox -->{% endif %}
          </div>
          <!-- end status-meta -->
      </div>
      <!-- end status -->{% endif %}