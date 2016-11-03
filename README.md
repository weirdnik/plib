# PLIB Engine 0.2

## About

This is an engine for running Twitter lookalike based on look, feel and features of now defunct BLIP.pl website.

## About BLIP features

Blip was a microblogging site loosely based on Twitter with changes that made it much more conversation-friendly:

* Instead of `@username`, users are referenced by `^username`. This makes sense in the context of messages.

* `^username` creates a mention a'la `@mention`.

* Mentions, messages and notifications are integral part of the timeline.

* `>username message` sends user `username` a **public** message (that can be seen on the user's timeline).

* `>>username message` sends user `username` a **private** message (only the sender and recipient can see it on their timelines).

* There is no separate message box.

* `#hashtags` work more like IRC channels. An user can subscribe a hashtag and all tagged statuses (but not messages) will show on his timeline.

* Users can ignore `#hashtags` -- statuses from followed users tagged with an ignored hashtags won't show on the subscriber's timeline.

* Users can quote the statuses with the body of the status being seen as a tooltip (this was implemented long before Twitter allowed quoting).

### Not implemented BLIP features

* BLIP was displaying a list of last ten logged in visitors who displayed the user's cockpit. This is not implemented in Plib.

* BLIP had a feature of sending and receiving statuses and messages through XMPP. This is not implemented in Plib.

* BLIP had an option to receive voice messages and MMS messages with pictures. This is not implemented in Plib.

* API.

## History

BLIP.pl was written by Marcin Jagodziński (`^reuptake`) and Zbigniew Sobiecki (`^kodz`) and operated from 2007 to 2013. In the meantime it was sold to Gadu-Gadu S.A.

During its operation, BLIP managed to attract a vibrant and active user community.

Plib was written in frenzy in summer 2013 as Gadu Gadu S.A. announced sunsetting of BLIP. Plib (a reverse of 'BLIP', get it?) was used to run Plum.ME, which in turn went defunct in early spring of 2015 due to low usage numbers.

## Architecture

Plib engine is a Django LAMP/LAPP application (*project* in Django parlance) with the following components (*Django apps*):

* `profile` -- user management (registration) and profile display with status archive, user subscriptions (followings) and ignores;

* `cockpit` -- main user interface -- the cockpit (timeline), creation, liking, unliking and deletion of user statuses;

* `main` -- the front page of the site, with image and status feeds;

* `blip` -- BLIP archive importer, the archiver part (utilizing Robert Maron's scripts) is working, the integration part is missing;

* `url` -- URL shortener, stub, not working.

BLIP had a complicated architecture based on a message broker system, Plib is database driven (and mostly database agnostic due to Django ORM).

## Deployment

In its final form, Plib should be deployed using a WSGI manager (preferably `gunicorn`) running behind a reverse proxy. Apache was utilized for this in production. Static files (all paths starting with `/static`) should be served directly through Apache, while the active URL-s should be passing to a WSGI manager. Example apache configuration utilizing Django WSGI interface directly is stored in the `apache.cfg` file. 

## TODO

* Plib was written and deployed as Plum.ME using Django 1.3 and 1.4 features. The main TODO is to port it to a modern Django version.

* The visitors list is missing from the cockpit.

* The URL shortener is missing.

* Separate message box (aggregation of private and public direct messages) would be useful.

* The frontend needs much work. It was coded by someone (`^alex`) with only superificial knowledge of frontend programming with some CSS fixes from other users.

* BLIP had an extensive API used by independent mobile apps. There is no API.

## Authors

The main programmer of Plib 0.1 was `^alex`, with `^cain` and `^brand` doing frontend work. Maciej Orliński did some basic work on status archives (*bliplogs*).

### Icons

The blue icons utilized as placeholders come from the excellent Iconic set by P. J. Onori (@somerandomdude on GitHub and Twitter) who gave them out on (CC) BY-SA licence. The set is avaliable at <http://somerandomdude.com/work/iconic>. Thanks! 

## Licence

Plib microblogging engine

Copyright (C) 2016 Alexander Gütsche

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.