from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from app import app, db, login_manager
from models import User, MaintenanceLog, WorkOrder, Task
from utils import generate_work_order, send_urgent_notification
from werkzeug.security import generate_password_hash
from sqlalchemy import func
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            if not user:
                flash('Username not found. Please check your username and try again.', 'error')
            else:
                flash('Invalid password. Please try again.', 'error')
        print(f"Login attempt: Username: {username}, User found: {user is not None}, Password correct: {user and user.check_password(password)}")
    return render_template('index.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    maintenance_count = MaintenanceLog.query.filter_by(user_id=current_user.id).count()
    work_order_count = WorkOrder.query.filter_by(created_by=current_user.id).count()
    task_count = Task.query.filter_by(user_id=current_user.id).count()
    
    task_stats = db.session.query(
        Task.status, func.count(Task.id)
    ).filter_by(user_id=current_user.id).group_by(Task.status).all()
    
    work_order_stats = db.session.query(
        WorkOrder.status, func.count(WorkOrder.id)
    ).filter_by(created_by=current_user.id).group_by(WorkOrder.status).all()
    
    return render_template('dashboard.html', 
                           maintenance_count=maintenance_count,
                           work_order_count=work_order_count,
                           task_count=task_count,
                           task_stats=dict(task_stats),
                           work_order_stats=dict(work_order_stats))

@app.route('/maintenance', methods=['GET', 'POST'])
@login_required
def maintenance():
    if request.method == 'POST':
        log = MaintenanceLog(
            date=request.form['date'],
            lot=request.form['lot'],
            details=request.form['details'],
            user_id=current_user.id
        )
        db.session.add(log)
        db.session.commit()
        
        work_order = generate_work_order(log)
        
        if work_order.priority == 'Urgent':
            send_urgent_notification(work_order)
        
        flash('Maintenance log added successfully')
        return redirect(url_for('maintenance'))
    
    logs = MaintenanceLog.query.filter_by(user_id=current_user.id).order_by(MaintenanceLog.date.desc()).all()
    return render_template('maintenance.html', logs=logs)

@app.route('/workorders')
@login_required
def workorders():
    orders = WorkOrder.query.filter_by(created_by=current_user.id).order_by(WorkOrder.created_at.desc()).all()
    return render_template('workorders.html', orders=orders)

@app.route('/workorders/create', methods=['GET', 'POST'])
@login_required
def create_workorder():
    if request.method == 'POST':
        work_order = WorkOrder(
            title=request.form['title'],
            description=request.form['description'],
            task=request.form['task'],
            status=request.form['status'],
            priority=request.form['priority'],
            due_date=datetime.strptime(request.form['due_date'], '%Y-%m-%d'),
            assigned_to=request.form['assigned_to'],
            created_by=current_user.id
        )
        db.session.add(work_order)
        db.session.commit()
        flash('Work order created successfully')
        return redirect(url_for('workorders'))
    
    users = User.query.all()
    return render_template('create_workorder.html', users=users)

@app.route('/workorders/<int:id>')
@login_required
def view_workorder(id):
    work_order = WorkOrder.query.get_or_404(id)
    return render_template('view_workorder.html', work_order=work_order)

@app.route('/workorders/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_workorder(id):
    work_order = WorkOrder.query.get_or_404(id)
    if request.method == 'POST':
        work_order.title = request.form['title']
        work_order.description = request.form['description']
        work_order.task = request.form['task']
        work_order.status = request.form['status']
        work_order.priority = request.form['priority']
        work_order.due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d')
        work_order.assigned_to = request.form['assigned_to']
        db.session.commit()
        flash('Work order updated successfully')
        return redirect(url_for('view_workorder', id=work_order.id))
    
    users = User.query.all()
    return render_template('edit_workorder.html', work_order=work_order, users=users)

@app.route('/workorders/<int:id>/delete', methods=['POST'])
@login_required
def delete_workorder(id):
    work_order = WorkOrder.query.get_or_404(id)
    db.session.delete(work_order)
    db.session.commit()
    flash('Work order deleted successfully')
    return redirect(url_for('workorders'))

@app.route('/tasks')
@login_required
def tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.due_date).all()
    assigned_work_orders = WorkOrder.query.filter_by(assigned_to=current_user.id).order_by(WorkOrder.due_date).all()
    return render_template('tasks.html', tasks=tasks, assigned_work_orders=assigned_work_orders)

@app.route('/api/update_task_status', methods=['POST'])
@login_required
def update_task_status():
    task_id = request.json['task_id']
    new_status = request.json['status']
    task = Task.query.get(task_id)
    if task and task.user_id == current_user.id:
        task.status = new_status
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 400

@app.route('/api/chart_data')
@login_required
def chart_data():
    task_stats = db.session.query(
        Task.status, func.count(Task.id)
    ).filter_by(user_id=current_user.id).group_by(Task.status).all()
    
    maintenance_stats = db.session.query(
        func.to_char(MaintenanceLog.date, 'YYYY-MM').label('month'),
        func.count(MaintenanceLog.id)
    ).filter_by(user_id=current_user.id).group_by('month').order_by('month').limit(6).all()
    
    work_order_stats = db.session.query(
        WorkOrder.status, func.count(WorkOrder.id)
    ).filter_by(created_by=current_user.id).group_by(WorkOrder.status).all()
    
    return jsonify({
        'task_stats': dict(task_stats),
        'maintenance_stats': dict(maintenance_stats),
        'work_order_stats': dict(work_order_stats)
    })
