// Tab functionality
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });
    event.currentTarget.classList.add('active');
}

// Investor form submission
document.getElementById('investor-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Basic validation
    const email = document.getElementById('investor-email').value;
    const password = document.getElementById('investor-password').value;
    
    if (!email || !password) {
        alert('Please fill in all required fields');
        return;
    }
    
    try {
        // First register the user
        const userResponse = await fetch('http://localhost:8000/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email,
                password: password,
                user_type: 'investor'
            })
        });
        
        if (!userResponse.ok) {
            const error = await userResponse.json();
            throw new Error(error.detail || 'Registration failed');
        }
        
        const user = await userResponse.json();
        
        // Now register the investor with documents
        const formData = new FormData();
        formData.append('user_id', user.id);
        formData.append('first_name', document.getElementById('investor-first-name').value);
        formData.append('last_name', document.getElementById('investor-last-name').value);
        formData.append('date_of_birth', document.getElementById('investor-dob').value);
        formData.append('phone_number', document.getElementById('investor-phone').value);
        formData.append('id_document_type', document.getElementById('investor-id-type').value);
        formData.append('id_document_number', document.getElementById('investor-id-number').value);
        formData.append('address', document.getElementById('investor-address').value);
        formData.append('tax_number', document.getElementById('investor-tax-number').value);
        formData.append('id_document_front', document.getElementById('investor-id-front').files[0]);
        formData.append('id_document_back', document.getElementById('investor-id-back').files[0]);
        formData.append('selfie_with_id', document.getElementById('investor-selfie').files[0]);
        
        const investorResponse = await fetch('http://localhost:8000/register/investor', {
            method: 'POST',
            body: formData
        });
        
        if (!investorResponse.ok) {
            const error = await investorResponse.json();
            throw new Error(error.detail || 'Investor registration failed');
        }
        
        const result = await investorResponse.json();
        alert('Registration successful! Please wait for verification.');
        window.location.href = 'login.html';
        
    } catch (error) {
        alert('Error: ' + error.message);
    }
});

// Business form submission
document.getElementById('business-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Basic validation
    const email = document.getElementById('business-email').value;
    const password = document.getElementById('business-password').value;
    
    if (!email || !password) {
        alert('Please fill in all required fields');
        return;
    }
    
    try {
        // First register the user
        const userResponse = await fetch('http://localhost:8000/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email,
                password: password,
                user_type: 'business'
            })
        });
        
        if (!userResponse.ok) {
            const error = await userResponse.json();
            throw new Error(error.detail || 'Registration failed');
        }
        
        const user = await userResponse.json();
        
        // Now register the business with documents
        const formData = new FormData();
        formData.append('user_id', user.id);
        formData.append('company_name', document.getElementById('company-name').value);
        formData.append('registration_number', document.getElementById('registration-number').value);
        formData.append('registration_date', document.getElementById('registration-date').value);
        formData.append('tax_number', document.getElementById('tax-number').value);
        formData.append('legal_address', document.getElementById('legal-address').value);
        formData.append('physical_address', document.getElementById('physical-address').value);
        formData.append('business_type', document.getElementById('business-type').value);
        formData.append('industry', document.getElementById('industry').value);
        formData.append('director_first_name', document.getElementById('director-first-name').value);
        formData.append('director_last_name', document.getElementById('director-last-name').value);
        formData.append('director_dob', document.getElementById('director-dob').value);
        formData.append('director_id_number', document.getElementById('director-id-number').value);
        formData.append('phone_number', document.getElementById('business-phone').value);
        formData.append('email', document.getElementById('business-email-2').value);
        formData.append('ownership_structure', document.getElementById('ownership-structure').value);
        formData.append('website', document.getElementById('website').value);
        formData.append('director_id_document', document.getElementById('director-id-document').files[0]);
        formData.append('director_selfie', document.getElementById('director-selfie').files[0]);
        formData.append('company_registration_certificate', document.getElementById('registration-certificate').files[0]);
        formData.append('tax_registration_certificate', document.getElementById('tax-certificate').files[0]);
        
        const businessResponse = await fetch('http://localhost:8000/register/business', {
            method: 'POST',
            body: formData
        });
        
        if (!businessResponse.ok) {
            const error = await businessResponse.json();
            throw new Error(error.detail || 'Business registration failed');
        }
        
        const result = await businessResponse.json();
        alert('Registration successful! Please wait for verification.');
        window.location.href = 'login.html';
        
    } catch (error) {
        alert('Error: ' + error.message);
    }
});