const errorMarkOpenTag = '<mark style="color: red; font-size:large; border-radius: 4px; padding: 5px 10px"> <i class="fas fa-exclamation-circle"> </i>';
const successMarkOpenTag = '<mark style="color: green; font-size:large; border-radius: 4px; padding: 5px 10px"> <i class="fas fa-check-circle"> </i>';


// Add event listeners to input fields for Enter key press
const loginEmail = document.getElementById('login_email');
const loginPwd = document.getElementById('login_pwd');
loginEmail.addEventListener('keypress', handleEnterKeyPress);
loginPwd.addEventListener('keypress', handleEnterKeyPress);

function handleEnterKeyPress(event) {
    if (event.key === 'Enter') {
        connect();
    }
}


// Function to connect via login credentials
function connect() {
    const email = document.getElementById("login_email").value;
    const pwd = document.getElementById("login_pwd").value;
    if (email == '' || !email.includes('@')) {
        document.getElementById("error_message-1").innerHTML = errorMarkOpenTag + ' Please enter a valid email address</mark>';
    } else if (pwd == "") {
        document.getElementById("error_message-1").innerHTML = errorMarkOpenTag + ' Please enter your password</mark>';
    } else {
        document.getElementById("error_message-1").innerHTML = '&nbsp;';
        fetch('/login', {
            method: "POST",
            body: JSON.stringify({ 'email': email, 'password': pwd }),
        }).then((response) => {
            if (!response.ok) {
                throw new Error();
            }
            return response.json();
        }).then(data => {
            if (data.status == 'Error') {
                document.getElementById("error_message-1").innerHTML = errorMarkOpenTag + ' ' + data.message + '</mark>';
            } else {
                document.location.href = data.href;
            }
        })
    }
}