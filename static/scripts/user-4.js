const errorMarkOpenTag = '<mark style="color: red; font-size:large; border-radius: 4px; padding: 5px 10px"> <i class="fas fa-exclamation-circle"> </i>';
const successMarkOpenTag = '<mark style="color: green; font-size:large; border-radius: 4px; padding: 5px 10px"> <i class="fas fa-check-circle"> </i>';


// Submits user contact information through a POST request.
function submitUserContact(email) {
    const subject = document.getElementById('subject').value;
    const message = document.getElementById('message').value;
    if (subject == '' || message == '') {
        document.getElementById('error_message-1').innerHTML =M + ' Please fill in all fields before submitting the form</mark>';
    } else {
        document.getElementById('error_message-1').innerHTML = "&nbsp;";
        fetch('/contact', {
            method: 'POST',
            body: JSON.stringify({ 'email': email, 'subject': subject, 'message': message }),
        }).then(response => {
            if (!response.ok) {
                throw new Error();
            }
            return response.json();
        }).then(data => {
            document.getElementById('response').innerHTML = data.status;
            document.getElementById('message').value = '';
            document.getElementById('subject').value = '';
            $('#response_model').modal('show');
        }).catch(error => {
            console.log(error);
        });
    }
}