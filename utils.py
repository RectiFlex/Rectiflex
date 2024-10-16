from models import WorkOrder, db
from app import socketio
from flask import url_for
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_work_order(maintenance_log):
    # Simple logic to generate a work order based on maintenance log
    is_urgent = "urgent" in maintenance_log.details.lower() or "immediate attention" in maintenance_log.details.lower()
    priority = "Urgent" if is_urgent else "Normal"
    
    work_order = WorkOrder(
        title=f"{'Urgent: ' if is_urgent else ''}Maintenance required for Lot {maintenance_log.lot}",
        description=f"Based on maintenance log: {maintenance_log.details}",
        status="Pending",
        priority=priority,
        created_by=maintenance_log.user_id
    )
    db.session.add(work_order)
    db.session.commit()

    logger.info(f"Work order created: {work_order.id}, Is urgent: {is_urgent}")

    # Send a notification for all work orders, with emphasis on urgent ones
    send_notification(
        work_order.title,
        'danger' if is_urgent else 'info',
        {
            'id': work_order.id,
            'description': work_order.description,
            'priority': work_order.priority,
            'url': url_for('view_workorder', id=work_order.id)
        }
    )

def send_notification(message, category, data=None):
    logger.info(f"Sending notification: {message}, Category: {category}, Data: {data}")
    socketio.emit('notification', {
        'message': message,
        'category': category,
        'data': data
    }, namespace='/notifications')
    logger.info("Notification sent")

def send_urgent_notification(work_order):
    send_notification(
        f"Urgent: New work order for Lot {work_order.maintenance_log.lot}",
        'danger',
        {
            'id': work_order.id,
            'description': work_order.description,
            'priority': work_order.priority,
            'url': url_for('view_workorder', id=work_order.id)
        }
    )
