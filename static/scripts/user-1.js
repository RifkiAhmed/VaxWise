let childId;
const errorMarkOpenTag = '<mark style="color: red; font-size:large; border-radius: 4px; padding: 5px 10px"> <i class="fas fa-exclamation-circle"> </i>';
const successMarkOpenTag = '<mark style="color: green; font-size:large; border-radius: 4px; padding: 5px 10px"> <i class="fas fa-check-circle"> </i>';


// Function to submit the addition of a child after form validation
function submitAddChild(parentId, parentLastName) {
    const firstName = document.getElementById('add_child_firstName').value;
    const birthdate = document.getElementById('add_child_birthday').value;
    const date = new Date(birthdate);
    const currentDate = new Date();
    if (firstName == '') {
        document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' Please enter your child first name</mark>';
    } else if (birthdate == '') {
        document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' Please enter your child birtdate</mark>';
    } else if (date > currentDate) {
        document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' Please enter a valid child birthdate</mark>';
    } else {
        document.getElementById('error_message-1').innerHTML = '&nbsp;';
        fetch('/child', {
            method: 'POST',
            body: JSON.stringify({ 'first_name': firstName, 'last_name': parentLastName, 'birthdate': birthdate, 'parent_id': parentId }),
        }).then(response => {
            document.location.href = '/';
        })
    }
}


// Function to display the modal for updating child information
function showUpdateChildModal(id) {
    childId = id;
    fetch('/child/' + id, {
        method: 'GET',
    }).then(response => {
        if (!response.ok) {
            throw new Error('');
        }
        return response.json();
    }).then(data => {
        document.getElementById('update_child_firstName').value = data.first_name;
        const birthdate = new Date(data.birthdate);
        document.getElementById('update_child_birthday').value = birthdate.toISOString().split('T')[0];
        $('#update_child_model').modal('show');
    }).catch(error => {
        console.log(error);
    });
}


// Function to submit updated child information after form validation
function submitUpdateChild() {
    const firstName = document.getElementById('update_child_firstName').value;
    const birthdate = document.getElementById('update_child_birthday').value;
    const date = new Date(birthdate);
    const currentDate = new Date();
    if (firstName == '') {
        document.getElementById('error_message-2').innerHTML = errorMarkOpenTag + ' Please enter your child first name</mark>';
    } else if (birthdate == '') {
        document.getElementById('error_message-2').innerHTML = errorMarkOpenTag + ' Please enter your child birthdate</mark>';
    } else if (date > currentDate) {
        document.getElementById('error_message-2').innerHTML = errorMarkOpenTag + ' Please enter a valid child birthdate</mark>';
    } else {
        document.getElementById('error_message-2').innerHTML = '&nbsp;';
        fetch('/child', {
            method: 'PUT',
            body: JSON.stringify({ 'id': childId, 'first_name': firstName, 'birthdate': birthdate }),
        }).then(response => {
            document.location.href = '/';
        })
    }
}


// Function to display the delete child confirmation modal
function showDeleteChildModal(id) {
    childId = id;
    fetch('/child/' + id, {
        method: 'GET',
    }).then(response => {
        if (!response.ok) {
            throw new Error('');
        }
        return response.json();
    }).then(data => {
        document.getElementById('delete_child_fullName').innerHTML = 'Are you sure you want to remove your child, ' + data.first_name + ' ?';
        $('#delete_child_model').modal('show');
    }).catch(error => {
        console.log(error);
    });
}


// Function to submit deletion of a child
function submitDeleteChild() {
    fetch('/child/' + childId, {
        method: 'DELETE',
    }).then(response => {
        if (!response.ok) {
            throw new Error('');
        }
    }).then(data => {
        document.location.href = '/';
    }).catch(error => {
        console.log(error);
    });
}


// Function to display vaccine description
function showVaccineDescription(id) {
    fetch('/vaccine/' + id, {
        method: 'GET',
    }).then(response => {
        if (!response.ok) {
            throw new Error();
        }
        return response.json();
    }).then(data => {
        document.getElementById('vaccine_denomination').innerHTML = 'Vaccine against : ' + data.denomination;
        document.getElementById('vaccine_description').innerHTML = data.description;
        const ul = document.getElementById('dose_description');
        while (ul.firstChild) {
            ul.removeChild(ul.firstChild);
        }
        data.doses.forEach(dose => {
            const li = document.createElement('li');
            li.innerHTML = '<strong>' + dose[0] + '</strong> : in ' + dose[1] + ' day(s)';
            ul.appendChild(li);
        });
        $('#vaccine_description_model').modal('show');
    }).catch(error => {
        console.log(error);
    })
}
