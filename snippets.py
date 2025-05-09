CODE_SNIPPETS = [
    {
        "code": """def validate_login(username, password):
    # Check if user exists in database
    query = f"SELECT * FROM users WHERE username = '{username}'"
    result = db.execute(query)
    
    if result:
        # Check if password matches
        if result['password'] == password:
            return True
    return False""",
        "language": "python",
        "issue_lines": [2, 3],  # SQL injection vulnerability
        "should_reject": True,
        "explanation": "SQL injection vulnerability: username is inserted directly into the query."
    },
    {
        "code": """function processPayment(amount) {
    // Validate amount
    if (amount <= 0) {
        return "Invalid amount";
    }
    
    // Process the payment
    return chargeCard(amount);
}""",
        "language": "javascript",
        "issue_lines": [],  # No obvious security issues
        "should_reject": False,
        "explanation": "This code is secure as it validates the input before processing."
    },
    {
        "code": """def generate_password_reset_token():
    import random
    # Generate a 6-digit token
    token = random.randint(100000, 999999)
    return token""",
        "language": "python",
        "issue_lines": [2, 4],  # Weak random number for security token
        "should_reject": True,
        "explanation": "Using predictable random numbers for security tokens is insecure. Should use cryptographically secure random numbers."
    },
    {
        "code": """public void executeCommand(String userInput) {
    // Execute system command
    Runtime runtime = Runtime.getRuntime();
    Process process = runtime.exec("ls " + userInput);
    
    // Return the output
    BufferedReader reader = new BufferedReader(
        new InputStreamReader(process.getInputStream()));
    // Process output...
}""",
        "language": "java",
        "issue_lines": [3, 4],  # Command injection vulnerability
        "should_reject": True,
        "explanation": "Command injection vulnerability: user input is directly appended to a system command."
    },
    {
        "code": """def hash_password(password):
    import hashlib
    # Generate a random salt
    salt = os.urandom(32)
    # Hash the password with the salt
    hash = hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        salt, 
        100000
    )
    return salt, hash""",
        "language": "python",
        "issue_lines": [],  # No security issues
        "should_reject": False,
        "explanation": "Correctly hashes passwords using PBKDF2 with a secure salt."
    },
    {
        "code": """app.post('/api/reset-password', (req, res) => {
    const { token, newPassword } = req.body;
    // Validate token exists in DB
    const user = findUserByToken(token);
    
    if (user) {
        // Update password
        user.password = newPassword;
        saveUser(user);
        res.send({ success: true });
    } else {
        res.status(400).send({ error: 'Invalid token' });
    }
});""",
        "language": "javascript",
        "issue_lines": [6, 7],  # Storing password in plaintext
        "should_reject": True,
        "explanation": "Password is stored without hashing, which is a serious security risk."
    },
    {
        "code": """def upload_file(request):
    uploaded_file = request.FILES['file']
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'application/pdf']
    if uploaded_file.content_type not in allowed_types:
        return HttpResponse("Invalid file type", status=400)
    
    # Save file securely
    file_path = os.path.join(UPLOAD_DIR, secure_filename(uploaded_file.name))
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.read())
    
    return HttpResponse("File uploaded successfully")""",
        "language": "python",
        "issue_lines": [],  # No obvious security issues
        "should_reject": False,
        "explanation": "File upload is secure with content type validation and secure filename handling."
    }
]
