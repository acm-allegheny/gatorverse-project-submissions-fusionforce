document.addEventListener('DOMContentLoaded', function() {
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });

    // Skill tag input enhancement
    const skillInputs = document.querySelectorAll('input[name="skills"], input[name="required_skills"]');
    skillInputs.forEach(input => {
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ',') {
                e.preventDefault();
                const value = this.value.trim();
                if (value) {
                    const tags = value.split(',').map(tag => tag.trim());
                    this.value = tags.join(', ');
                }
            }
        });
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
    const collaborateButtons = document.querySelectorAll('[data-bs-toggle="modal"]');
    collaborateButtons.forEach(button => {
        button.addEventListener('click', function() {
            const projectId = this.dataset.projectId;
            const modal = document.getElementById('collaborateModal');
            if (modal) {
                modal.querySelector('form').action = `/request_collaboration/${projectId}`;
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