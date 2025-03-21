from flask import Blueprint, request, render_template, flash, redirect, url_for, session, current_app
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from models import db, User, Listing, Message, Transaction
from auth import login_required, admin_required

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}  # Add more extensions as needed

routes_bp = Blueprint('routes', __name__)

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# Home route
@routes_bp.route('/')
def index():
    recent_listings = Listing.query.filter_by(status='available').order_by(Listing.created_at.desc()).limit(8).all()
    return render_template('index.html', listings=recent_listings, now=datetime.utcnow(), datetime=datetime)

# User dashboard
@routes_bp.route('/dashboard')
@login_required
def dashboard():
    """Render the user dashboard with listings, messages, and transactions."""
    user_id = session['user_id']
    user_listings = Listing.query.filter_by(seller_id=user_id).all()
    sent_messages = Message.query.filter_by(sender_id=user_id).all()
    received_messages = Message.query.filter_by(receiver_id=user_id).all()
    conversations = set(msg.receiver_id for msg in sent_messages) | set(msg.sender_id for msg in received_messages)
    conversations = [User.query.get(uid) for uid in conversations if uid != user_id]
    buyer_transactions = Transaction.query.filter_by(buyer_id=user_id).all()
    seller_transactions = Transaction.query.join(Listing).filter(Listing.seller_id == user_id).all()
    return render_template('dashboard.html', listings=user_listings, conversations=conversations, buyer_transactions=buyer_transactions, seller_transactions=seller_transactions)

# Book listings
@routes_bp.route('/listings')
def listings():
    """Render the listings page with optional filters."""
    subject = request.args.get('subject')
    course = request.args.get('course')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    query = request.args.get('q')
    
    listings_query = Listing.query.filter_by(status='available')
    
    if subject:
        listings_query = listings_query.filter(Listing.subject == subject)
    if course:
        listings_query = listings_query.filter(Listing.course == course)
    if min_price:
        listings_query = listings_query.filter(Listing.price >= float(min_price))
    if max_price:
        listings_query = listings_query.filter(Listing.price <= float(max_price))
    if query:
        listings_query = listings_query.filter(
            Listing.title.ilike(f'%{query}%') |
            Listing.author.ilike(f'%{query}%') |
            Listing.description.ilike(f'%{query}%')
        )
    
    listings = listings_query.order_by(Listing.created_at.desc()).all()
    subjects = db.session.query(Listing.subject).distinct().all()
    courses = db.session.query(Listing.course).distinct().all()
    
    return render_template(
        'listings.html',
        listings=listings,
        subjects=[s[0] for s in subjects if s[0]],
        courses=[c[0] for c in courses if c[0]],
        filter_subject=subject,
        filter_course=course,
        filter_min_price=min_price,
        filter_max_price=max_price,
        query=query
    )

# View a single listing
@routes_bp.route('/listing/<int:listing_id>')
def view_listing(listing_id):
    """Render the page for a single listing."""
    listing = Listing.query.get_or_404(listing_id)
    is_owner = session.get('user_id') == listing.seller_id
    return render_template('listing.html', listing=listing, is_owner=is_owner)

# Create a new listing
@routes_bp.route('/listing/new', methods=['GET', 'POST'])
@login_required
def new_listing():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        condition = request.form.get('condition')
        price = request.form.get('price')
        description = request.form.get('description')
        subject = request.form.get('subject')
        course = request.form.get('course')
        
        if not all([title, author, condition, price]):
            flash('Please fill out all required fields.', 'error')
            return redirect(url_for('routes.new_listing'))
        
        listing = Listing(
            title=title,
            author=author,
            condition=condition,
            price=float(price),
            description=description,
            subject=subject,
            course=course,
            seller_id=session['user_id']  # Ensure seller_id is set correctly
        )
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                listing.image_path = f"/static/uploads/{filename}"
        
        db.session.add(listing)
        db.session.commit()
        
        flash('Your listing has been created.', 'success')
        return redirect(url_for('routes.view_listing', listing_id=listing.id))
    
    return render_template('new_listing.html')

# Edit a listing
@routes_bp.route('/listing/<int:listing_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_listing(listing_id):
    """Handle the editing of a listing."""
    listing = Listing.query.get_or_404(listing_id)
    if session['user_id'] != listing.seller_id and session.get('user_role') != 'admin':
        flash('You do not have permission to edit this listing.', 'error')
        return redirect(url_for('routes.view_listing', listing_id=listing.id))
    
    if request.method == 'POST':
        listing.title = request.form.get('title')
        listing.author = request.form.get('author')
        listing.condition = request.form.get('condition')
        listing.price = float(request.form.get('price'))
        listing.description = request.form.get('description')
        listing.subject = request.form.get('subject')
        listing.course = request.form.get('course')
        
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                if listing.image_path:
                    old_file_path = os.path.join(current_app.root_path, listing.image_path.lstrip('/'))
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                listing.image_path = f"/static/uploads/{filename}"
        
        db.session.commit()
        flash('Your listing has been updated.', 'success')
        return redirect(url_for('routes.view_listing', listing_id=listing.id))
    
    return render_template('edit_listing.html', listing=listing)

# Delete a listing
@routes_bp.route('/listing/<int:listing_id>/delete', methods=['POST'])
@login_required
def delete_listing(listing_id):
    """Handle the deletion of a listing."""
    listing = Listing.query.get_or_404(listing_id)
    if session['user_id'] != listing.seller_id and session.get('user_role') != 'admin':
        flash('You do not have permission to delete this listing.', 'error')
        return redirect(url_for('routes.view_listing', listing_id=listing.id))
    
    if listing.image_path:
        file_path = os.path.join(current_app.root_path, listing.image_path.lstrip('/'))
        if os.path.exists(file_path):
            os.remove(file_path)
    
    db.session.delete(listing)
    db.session.commit()
    flash('Your listing has been deleted.', 'success')
    return redirect(url_for('routes.dashboard'))

# Messaging
@routes_bp.route('/messages/<int:user_id>')
@login_required
def messages(user_id):
    """Render the messaging interface between users."""
    current_user_id = session['user_id']
    other_user = User.query.get_or_404(user_id)
    messages = Message.query.filter(
        ((Message.sender_id == current_user_id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user_id))
    ).order_by(Message.created_at).all()
    
    for msg in messages:
        if msg.receiver_id == current_user_id and not msg.read:
            msg.read = True
    db.session.commit()
    
    return render_template('messages.html', messages=messages, other_user=other_user)

# Send a message
@routes_bp.route('/messages/send', methods=['POST'])
@login_required
def send_message():
    """Handle sending a message."""
    receiver_id = request.form.get('receiver_id')
    listing_id = request.form.get('listing_id')
    content = request.form.get('content')
    
    if not receiver_id or not content:
        flash('Message could not be sent.', 'error')
        return redirect(request.referrer or url_for('routes.dashboard'))
    
    message = Message(
        sender_id=session['user_id'],
        receiver_id=int(receiver_id),
        content=content,
        listing_id=int(listing_id) if listing_id else None
    )
    
    db.session.add(message)
    db.session.commit()
    flash('Message sent.', 'success')
    return redirect(url_for('routes.messages', user_id=receiver_id))

# Buy a book
@routes_bp.route('/buy/<int:listing_id>', methods=['POST'])
@login_required
def buy_book(listing_id):
    """Handle the purchase of a book."""
    listing = Listing.query.get_or_404(listing_id)
    if listing.status != 'available':
        flash('This book is no longer available.', 'error')
        return redirect(url_for('routes.view_listing', listing_id=listing.id))
    
    if listing.seller_id == session['user_id']:
        flash('You cannot buy your own book.', 'error')
        return redirect(url_for('routes.view_listing', listing_id=listing.id))
    
    transaction = Transaction(listing_id=listing.id, buyer_id=session['user_id'])
    listing.status = 'pending'
    db.session.add(transaction)
    db.session.commit()
    flash('Purchase initiated. Please coordinate with the seller for payment and pickup.', 'success')
    return redirect(url_for('routes.messages', user_id=listing.seller_id))

# Complete a transaction
@routes_bp.route('/transaction/<int:transaction_id>/complete', methods=['POST'])
@login_required
def complete_transaction(transaction_id):
    """Mark a transaction as completed."""
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.listing.seller_id != session['user_id']:
        flash('You do not have permission to complete this transaction.', 'error')
        return redirect(url_for('routes.dashboard'))
    
    transaction.status = 'completed'
    transaction.completed_at = datetime.utcnow()
    transaction.listing.status = 'sold'
    db.session.commit()
    flash('Transaction completed successfully.', 'success')
    return redirect(url_for('routes.dashboard'))

# Admin panel
@routes_bp.route('/admin')
@admin_required
def admin_panel():
    """Render the admin panel."""
    users = User.query.all()
    listings = Listing.query.all()
    transactions = Transaction.query.all()
    return render_template('admin.html', users=users, listings=listings, transactions=transactions)

# Admin update user
@routes_bp.route('/admin/user/<int:user_id>', methods=['POST'])
@admin_required
def admin_update_user(user_id):
    """Handle admin actions on users."""
    user = User.query.get_or_404(user_id)
    action = request.form.get('action')
    
    if action == 'make_admin':
        user.role = 'admin'
    elif action == 'remove_admin':
        user.role = 'user'
    elif action == 'delete':
        db.session.delete(user)
    
    db.session.commit()
    flash('User updated successfully.', 'success')
    return redirect(url_for('routes.admin_panel'))

# Admin update listing
@routes_bp.route('/admin/listing/<int:listing_id>', methods=['POST'])
@admin_required
def admin_update_listing(listing_id):
    """Handle admin actions on listings."""
    listing = Listing.query.get_or_404(listing_id)
    action = request.form.get('action')
    
    if action == 'delete':
        if listing.image_path:
            file_path = os.path.join(current_app.root_path, listing.image_path.lstrip('/'))
            if os.path.exists(file_path):
                os.remove(file_path)
        db.session.delete(listing)
    
    db.session.commit()
    flash('Listing updated successfully.', 'success')
    return redirect(url_for('routes.admin_panel'))