// Handle profile image errors with fallback initials
document.addEventListener('DOMContentLoaded', function() {
    function handleImageError(img) {
        const userName = img.getAttribute('data-user-name') || img.getAttribute('alt') || 'User';
        let initials = 'U';
        
        // Extract initials from user name
        const parts = userName.trim().split(' ').filter(part => part.length > 0);
        if (parts.length > 0) {
            initials = parts.map(part => part[0].toUpperCase()).join('').slice(0, 2);
        }
        
        // Create a styled div to replace the image
        const initialDiv = document.createElement('div');
        initialDiv.className = 'profile-initial';
        initialDiv.textContent = initials;
        initialDiv.style.width = img.getAttribute('width') || img.style.width || '140px';
        initialDiv.style.height = img.getAttribute('height') || img.style.height || '140px';
        initialDiv.style.borderRadius = '50%';
        initialDiv.style.display = 'flex';
        initialDiv.style.alignItems = 'center';
        initialDiv.style.justifyContent = 'center';
        initialDiv.style.backgroundColor = '#d0d0d0';
        initialDiv.style.color = '#333';
        initialDiv.style.fontWeight = 'bold';
        initialDiv.style.fontSize = '48px';
        initialDiv.style.border = img.style.border || '2px solid #ddd';
        initialDiv.style.objectFit = 'cover';
        
        img.replaceWith(initialDiv);
    }
    
    // Set error handlers for all profile images on the page
    const profileImages = document.querySelectorAll('.user-profile, [data-user-name]');
    profileImages.forEach(img => {
        if (img.tagName === 'IMG') {
            img.addEventListener('error', function() {
                handleImageError(this);
            });
        }
    });
});
