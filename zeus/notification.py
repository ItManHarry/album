from flask import url_for
from zeus.extensions import db
import uuid
from zeus.models import Notification
'''
    推送关注用户提醒
'''
def push_follow_notification(follower, receiver):
    message = 'User %s has followed you!!!' %follower.name
    notification = Notification(
        id=uuid.uuid4().hex,
        message=message,
        receiver=receiver
    )
    db.session.add(notification)
    db.session.commit()
'''
    推送取消关系用户提醒
'''
def push_unfollow_notification(follower, receiver):
    message = 'User %s do not follow you any longer!!!' %follower.name
    notification = Notification(
        id=uuid.uuid4().hex,
        message=message,
        receiver=receiver
    )
    db.session.add(notification)
    db.session.commit()