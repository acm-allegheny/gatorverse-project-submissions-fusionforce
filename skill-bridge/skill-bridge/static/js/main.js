document.addEventListener('DOMContentLoaded', function() {
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });

    // Skill tag input enhancement
    const skillInputs = document.querySelectorAll('input[name="skills"], input[name="required_skills"], input[name="tags"]');
    skillInputs.forEach(input => {
        // Add a container for displaying the tags
        const container = document.createElement('div');
        container.className = 'skill-tags-container d-flex flex-wrap mt-2';
        input.parentNode.insertBefore(container, input.nextSibling);

        // Add tags from existing values when page loads
        if (input.value) {
            const tags = input.value.split(',').map(tag => tag.trim()).filter(tag => tag);
            tags.forEach(tag => addTag(tag, container, input));
        }

        // Handle input events
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ',') {
                e.preventDefault();
                const value = this.value.trim();
                if (value) {
                    addTag(value, container, input);
                    this.value = '';
                }
            }
        });

        // Function to add a tag
        function addTag(text, container, input) {
            const tag = document.createElement('span');
            tag.className = 'badge bg-primary me-2 mb-2 p-2';
            tag.textContent = text;
            
            // Add remove button
            const removeBtn = document.createElement('i');
            removeBtn.className = 'bi bi-x-circle ms-1';
            removeBtn.style.cursor = 'pointer';
            removeBtn.addEventListener('click', function() {
                container.removeChild(tag);
                updateInputValue(container, input);
            });
            
            tag.appendChild(removeBtn);
            container.appendChild(tag);
            updateInputValue(container, input);
        }

        // Function to update the hidden input value
        function updateInputValue(container, input) {
            const tags = Array.from(container.querySelectorAll('.badge')).map(tag => {
                // Get only the text content, remove the "×" button text
                return tag.textContent.replace('×', '').trim();
            });
            input.value = tags.join(', ');
        }
    });

    // Project search functionality
    const searchInput = document.getElementById('projectSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const projects = document.querySelectorAll('.project-card');
            
            projects.forEach(project => {
                const title = project.querySelector('.card-title').textContent.toLowerCase();
                const description = project.querySelector('.card-text').textContent.toLowerCase();
                const skills = project.querySelector('.text-muted').textContent.toLowerCase();
                
                if (title.includes(searchTerm) || 
                    description.includes(searchTerm) || 
                    skills.includes(searchTerm)) {
                    project.style.display = '';
                } else {
                    project.style.display = 'none';
                }
            });
        });
    }

    // Profile image upload preview
    const imageUpload = document.getElementById('profileImage');
    if (imageUpload) {
        imageUpload.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    document.getElementById('profileImagePreview').src = e.target.result;
                }
                reader.readAsDataURL(file);
            }
        });
    }

    // Collaboration request handling
    const collaborateButtons = document.querySelectorAll('[data-bs-toggle="modal"][data-project-id]');
    collaborateButtons.forEach(button => {
        button.addEventListener('click', function() {
            const projectId = this.dataset.projectId;
            const modal = document.getElementById('collaborateModal');
            if (modal && projectId) {
                modal.querySelector('form').action = `/project/${projectId}/collaborate`;
            }
        });
    });

    // Loading state handling
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner"></span> Processing...';
            }
        });
    });

    // Notification system
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} notification`;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => notification.remove(), 500);
        }, 3000);
    }

    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Mobile menu toggle enhancement
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            this.classList.toggle('active');
        });
    }
});