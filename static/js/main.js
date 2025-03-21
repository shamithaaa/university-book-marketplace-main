document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            
            // Remove active class from all tabs and contents
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            // Add active class to current tab and content
            this.classList.add('active');
            document.getElementById(`${tabId}-content`).classList.add('active');
        });
    });

    // Flash message animations and close button
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        // Add slide down animation
        message.style.animation = 'slideDown 0.5s ease-out';
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            message.style.animation = 'slideUp 0.5s ease-out forwards';
            setTimeout(() => {
                message.style.display = 'none';
            }, 500);
        }, 5000);
    });
    
    const closeButtons = document.querySelectorAll('.close-btn');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const message = this.parentElement;
            message.style.animation = 'slideUp 0.5s ease-out forwards';
            setTimeout(() => {
                message.style.display = 'none';
            }, 500);
        });
    });

    // Enhance book listings
    const bookListItems = document.querySelectorAll('#books-list li');
    bookListItems.forEach(item => {
        // Extract book details
        const text = item.innerHTML;
        const titleAuthorPrice = text.split(' - ')[0];
        const actions = text.split(' - ')[1] || '';
        
        // Split title and author
        let title, author, price;
        
        if (titleAuthorPrice.includes(' by ')) {
            [title, author] = titleAuthorPrice.split(' by ');
            if (author.includes('$')) {
                [author, price] = author.split(' - $');
                price = '$' + price;
            }
        } else {
            title = titleAuthorPrice;
        }
        
        // Create new structure
        item.innerHTML = '';
        
        const bookInfo = document.createElement('div');
        bookInfo.className = 'book-info';
        
        const titleElem = document.createElement('div');
        titleElem.className = 'book-title';
        titleElem.textContent = title;
        bookInfo.appendChild(titleElem);
        
        if (author) {
            const authorElem = document.createElement('div');
            authorElem.className = 'book-author';
            authorElem.textContent = 'by ' + author;
            bookInfo.appendChild(authorElem);
        }
        
        if (price) {
            const priceElem = document.createElement('div');
            priceElem.className = 'book-price';
            priceElem.textContent = price;
            bookInfo.appendChild(priceElem);
        }
        
        item.appendChild(bookInfo);
        
        // Extract and add actions
        if (actions) {
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'book-actions';
            
            // Parse the actions HTML
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = actions;
            
            const links = tempDiv.querySelectorAll('a');
            links.forEach(link => {
                const newLink = document.createElement('a');
                newLink.href = link.href;
                newLink.textContent = link.textContent;
                
                if (link.textContent.trim().toLowerCase() === 'edit') {
                    newLink.className = 'edit-btn';
                } else if (link.textContent.trim().toLowerCase() === 'delete') {
                    newLink.className = 'delete-btn';
                }
                
                actionsDiv.appendChild(newLink);
            });
            
            item.appendChild(actionsDiv);
        }
    });

    // Enhance chat functionality
    const chatMessages = document.getElementById('messages');
    const messageInput = document.getElementById('message');
    const sendButton = document.querySelector('button');
    
    if (chatMessages && messageInput && sendButton) {
        // Style existing messages if any
        const existingMessages = chatMessages.querySelectorAll('p');
        existingMessages.forEach(msg => {
            const text = msg.textContent;
            if (text.startsWith('User')) {
                const parts = text.split(': ');
                const userId = parts[0].replace('User ', '');
                const messageText = parts.slice(1).join(': ');
                
                msg.className = 'message ' + (userId == sender_id ? 'sent' : 'received');
                msg.innerHTML = messageText + '<div class="message-time">' + new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) + '</div>';
            }
        });
        
        // Enhance send button
        sendButton.className = 'send-btn';
        sendButton.innerHTML = '<i class="fas fa-paper-plane"></i> Send';
        
        // Add message input container
        const inputContainer = document.createElement('div');
        inputContainer.className = 'chat-input-container';
        
        // Move elements to container
        const parent = messageInput.parentNode;
        parent.insertBefore(inputContainer, messageInput);
        inputContainer.appendChild(messageInput);
        inputContainer.appendChild(sendButton);
        
        // Override the sendMessage function for better UI
        window.sendMessage = function() {
            const message = messageInput.value.trim();
            
            if (message) {
                // Emit the message to the server
                socket.emit('message', {
                    sender_id: sender_id,
                    receiver_id: receiverId,
                    message: message
                });
                
                // Create and add message element with local timestamp
                const messageElem = document.createElement('div');
                messageElem.className = 'message sent';
                
                const messageText = document.createTextNode(message);
                messageElem.appendChild(messageText);
                
                const timeElem = document.createElement('div');
                timeElem.className = 'message-time';
                timeElem.textContent = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                messageElem.appendChild(timeElem);
                
                chatMessages.appendChild(messageElem);
                
                // Auto-scroll to the latest message
                chatMessages.scrollTop = chatMessages.scrollHeight;
                
                // Clear the input field
                messageInput.value = '';
            }
        };
        
        // Update socket message handler
        if (typeof socket !== 'undefined') {
            // Override the socket message handler
            socket.off('message');
            socket.on('message', function(data) {
                // Only add message if it's from the other user
                if (data.sender_id != sender_id) {
                    const messageElem = document.createElement('div');
                    messageElem.className = 'message received';
                    messageElem.textContent = data.message;
                    
                    const timeElem = document.createElement('div');
                    timeElem.className = 'message-time';
                    timeElem.textContent = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                    messageElem.appendChild(timeElem);
                    
                    chatMessages.appendChild(messageElem);
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }
            });
        }
        
        // Enter key to send message
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendMessage();
            }
        });
    }
    
    // Add responsiveness to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        // Add styles to form elements for better consistency
        const inputs = form.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            if (!input.classList.contains('btn')) {
                input.classList.add('form-input');
            }
        });
        
        // Style submit buttons
        const submitButtons = form.querySelectorAll('button[type="submit"]');
        submitButtons.forEach(button => {
            button.classList.add('btn');
        });
    });
    
    // Add header & footer if they don't exist
    if (!document.querySelector('header')) {
        const header = document.createElement('header');
        const container = document.createElement('div');
        container.className = 'container';
        
        const title = document.querySelector('h1');
        const titleText = title ? title.textContent : 'Campus Book Exchange';
        
        container.innerHTML = `
            <h1>${titleText}</h1>
            <nav>
                <a href="/">Home</a>
                <a href="/dashboard">Books</a>
                <a href="/add_book">Add Book</a>
            </nav>
        `;
        
        header.appendChild(container);
        document.body.insertBefore(header, document.body.firstChild);
        
        // Remove the original h1 if it exists
        if (title) {
            title.remove();
        }
    }
    
    if (!document.querySelector('footer')) {
        const footer = document.createElement('footer');
        footer.innerHTML = '<div class="container">Campus Book Exchange © ' + new Date().getFullYear() + '</div>';
        document.body.appendChild(footer);
    }
    
    // Style add book link on dashboard
    const addBookLink = document.querySelector('a[href*="add_book"]');
    if (addBookLink && !addBookLink.closest('nav')) {
        addBookLink.className = 'add-book-btn';
    }
    
    // Style back to dashboard link
    const backToDashboard = document.querySelector('a[href*="dashboard"]');
    if (backToDashboard && !backToDashboard.closest('nav')) {
        backToDashboard.className = 'back-btn';
        backToDashboard.textContent = 'Back to Dashboard';
    }
});

// Add CSS animation definitions
if (!document.getElementById('animation-styles')) {
    const styleSheet = document.createElement('style');
    styleSheet.id = 'animation-styles';
    styleSheet.textContent = `
        @keyframes slideUp {
            from { opacity: 1; transform: translateY(0); }
            to { opacity: 0; transform: translateY(-20px); }
        }
        
        @keyframes slideDown {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    `;
    document.head.appendChild(styleSheet);
}

// Font Awesome for icons
if (!document.getElementById('font-awesome')) {
    const fontAwesome = document.createElement('link');
    fontAwesome.id = 'font-awesome';
    fontAwesome.rel = 'stylesheet';
    fontAwesome.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css';
    document.head.appendChild(fontAwesome);
}