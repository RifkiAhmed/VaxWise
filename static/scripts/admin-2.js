const errorMarkOpenTag = '<mark style="color: red; font-size:large; border-radius: 4px; padding: 5px 10px"> <i class="fas fa-exclamation-circle"> </i>';
const successMarkOpenTag = '<mark style="color: green; font-size:large; border-radius: 4px; padding: 5px 10px"> <i class="fas fa-check-circle"> </i>';


// Function to add a new hospital
function addHospital(event) {
    // Prevent default form submission behavior
    event.preventDefault();

    let text = document.getElementById("hospital_name").value;
    if (text == '') {
        document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' Add Hospital Name</mark>';
    } else {
        // Fetch request to check if the hospital name already exists
        fetch('/hospital/' + text, {
            method: 'GET',
        }).then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        }).then(data => {
            if (data.status === 'Exist') {
                document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' This hospital name already exists</mark>';
            } else {
                document.getElementById('error_message-1').innerHTML = '&nbsp;';
                // POST request to add a new hospital
                fetch('/hospital', {
                    method: 'POST',
                    body: JSON.stringify({ 'name': text })
                })
                    .then((_res) => {
                        window.location.href = "/hospitals";
                    })
                    .catch(postError => {
                        console.error('Error with POST request:', postError);
                    });
            }
        }).catch(error => {
            console.error('There has been a problem with fetch operation:', error);
        });
    }
}


// Function to fetch data based on selected options
function fetchData() {
    let hospitalId = document.getElementById('hospital-5').value;
    let radios = document.getElementsByName('hospital_radio');

    let selectedValue = '';
    for (const radio of radios) {
        if (radio.checked) {
            selectedValue = radio.value;
            break;
        }
    }
    if (selectedValue == "nurses") {
        hospitalNurses(hospitalId);
    } else {
        hospitalVaccines(hospitalId);
    }
}


// Function to fetch nurses data for a hospital
function hospitalNurses(hospitalId) {
    let tbody = document.getElementById('table_nurses_body');
    fetch('/hospital/nurses', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id: hospitalId }),
    }).then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    }).then(data => {
        tbody.innerHTML = '';
        data.forEach(nurse => {
            let tr = document.createElement('tr');
            let td = document.createElement('td');
            td.innerHTML = '<h6>' + nurse.first_name + ' ' + nurse.last_name + '</h6>';
            tr.appendChild(td);
            tbody.appendChild(tr);
        });
        // Hide vaccines info and display nurses info
        document.getElementById('vaccines_info').style.display = "none";
        document.getElementById('nurses_info').style.display = "table";
    }).catch(error => {
        console.error('There has been a problem with fetch operation:', error);
    });
}


// Function to fetch vaccine data for a hospital
function hospitalVaccines(id) {
    let tbody = document.getElementById('table_vaccines_body');
    fetch('/hospital/vaccines', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id: id }),
    }).then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    }).then(data => {
        tbody.innerHTML = '';
        data.forEach(item => {
            let tr = document.createElement('tr');
            let td1 = document.createElement('td');
            let td2 = document.createElement('td');
            td1.innerHTML = '<h6>' + item.denomination + '</h6>';
            td2.innerHTML = '<h6>' + item.quantity + '</h6>';
            tr.appendChild(td1);
            tr.appendChild(td2);
            tr.style.padding = "20px";
            tbody.appendChild(tr);
        });
        // Hide nurses info and display vaccines info
        document.getElementById('nurses_info').style.display = "none";
        document.getElementById('vaccines_info').style.display = "table";

    }).catch(error => {
        console.error('There has been a problem with fetch operation:', error);
    });
}
