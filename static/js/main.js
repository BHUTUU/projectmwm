// const userPhoto = document.querySelector('#userPhoto');
// const userPhotoShow = document.querySelector('#userPhotoShow');
// userPhoto.addEventListener('input', ()=>{
//   const userPhotoInput = userPhoto.value;
//   userPhotoShow.innerHTML = `${userPhotoInput}`;
// });
// var regForm = document.getElementById('registrationform');
function updateScreenSize() {
    const width = window.innerWidth;
    const emailDiv = document.getElementById('email');
    const newWidth = width - 550;
    const minWidth = 250;
    emailDiv.style.width = (newWidth > minWidth ? newWidth : minWidth) + 'px';
}
updateScreenSize();
document.getElementById('submitbutton').disabled = true;
window.addEventListener('resize', updateScreenSize);
localStorage.setItem('emailVerified', false);
sessionStorage.setItem('verificlick', true);
document.getElementById('verifyOtpBtn').addEventListener('submit', function(event) {
    event.preventDefault();
});
document.getElementById('resendOtpBtn').addEventListener('submit', function(event) {
    event.preventDefault();
});
document.getElementById('verifyEmailBtn').addEventListener('submit', function(event) {
    event.preventDefault();
});
document.getElementById('verifyEmailBtn').addEventListener('click', function () {
  emailValue = document.getElementById('email').value;
  if(sessionStorage.getItem('verificlick').toString() == "true") {
    sessionStorage.setItem('verificlick', false);
    document.getElementById('verifyEmailBtn').innerText = "Edit";
    formData = new FormData();
    formData.append('email', emailValue);
    if(emailValue != '' && emailValue != null) {
        fetch('/sendOTP', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                alert('OTP sent successfully')
            } else {
                alert("Failed to send OTP");
            }
        })
        .catch(error => {
            console.error('Fetch error:', error);
            alert("An error occurred while sending OTP");
        });
        document.getElementById('otpPopup').style.display = 'block';
    } else {
      sessionStorage.setItem('verificlick', true);
      document.getElementById('verifyEmailBtn').innerText = 'Verify'
      alert('Please enter a valid email address');
    }
  } else {
    sessionStorage.setItem('verificlick', true);
    document.getElementById('otpPopup').style.display = 'none';
    document.getElementById('verifyEmailBtn').innerText = 'Verify'
  }
});

document.getElementById('verifyOtpBtn').addEventListener('click', function () {
    emailValue = document.getElementById('email').value;
    enteredOTP = document.getElementById('otp').value;
    if (enteredOTP == '' || enteredOTP == null) {
        alert('Please enter a valid OTP');
        return;
    }
    formData = new FormData();
    formData.append('email', emailValue);
    formData.append('otp', enteredOTP);
    fetch('/verifyOTP', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            alert('OTP match successfull')
            document.getElementById('otpPopup').style.display = 'none';
            document.getElementById('verificationStatus').textContent = 'Email ' + emailValue + ' is verified';
            document.getElementById('verifyEmailBtn').innerText = 'verified!';
            document.getElementById('verifyEmailBtn').disabled = true;
            document.getElementById('email').disabled = true;
            document.getElementById('submitbutton').disabled = false;
        } else {
            alert("OTP match failed");
            return;
        }
    })
    .catch(error => {
        console.error('Fetch error:', error);
        alert("Something went wrong");
        return;
    });
});

document.getElementById('resendOtpBtn').addEventListener('click', function () {
    emailValue = document.getElementById('email').value;
    formData = new FormData();
    formData.append('email', emailValue);
    fetch('/sendOTP', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            alert('OTP has been resent.');
        } else {
            alert("Failed to send OTP");
        }
    })
    .catch(error => {
        console.error('Fetch error:', error);
        alert("An error occurred while sending OTP");
    });
});
document.getElementById('submitbutton').addEventListener('click', function(event) {
  event.preventDefault();
  try {
      var userPhoto = document.getElementById('userPhoto');
      var userFullName = document.getElementById('fullname').value;
      var userEmail = document.getElementById('email').value;
      var password = document.getElementById('password').value;
      var dateOfBirth = document.getElementById('dateofbirth').value;
      var mobileNumber = document.getElementById('mobilenumber').value;
      var alternateNumber = document.getElementById('alternatemobile').value;
      var aadharnumber = document.getElementById('aadharnumber').value;
      var aadhaImage = document.getElementById('aadharimage');
      var pannumber = document.getElementById('pancardnumber').value;
      var panImage = document.getElementById('panimage');

      const userPhotoFile = userPhoto.files[0];
      const aadhaImageFile = aadhaImage.files[0];
      const panImageFile = panImage.files[0];

      const formData = new FormData();
      formData.append('userphoto', userPhotoFile);
      formData.append('fullname', userFullName);
      formData.append('useremail', userEmail);
      formData.append('password', password);
      formData.append('dateofbirth', dateOfBirth);
      formData.append('mobilenumber', mobileNumber);
      formData.append('alternatemobile', alternateNumber);
      formData.append('aadharnumber', aadharnumber);
      formData.append('aadharimagefile', aadhaImageFile);
      formData.append('pannumber', pannumber);
      formData.append('panimagefile', panImageFile);

      fetch('/submitregistereddata', {
          method: 'POST',
          body: formData
      })
      .then(response => response.json())
      .then(data => {
          if (data.status === "success") {
            alert(data.id, data.session_token)                               //to be removed after completion of the the website
            localStorage.setItem('idofgegestration', data.id);
            sessionStorage.setItem('sessionToken', data.session_token);
            // window.location.href = '/bankDetails'
            const bankAuthForm = new FormData();
            bankAuthForm.append('session_token', data.session_token);
            if(data.id != "" && data.id != null && data.id != undefined) {
                fetch('/bankDetails?session_token='+data.session_token, {
                    method: 'GET'
                })
                .then(response => response.text())
                .then(html => {
                    // Do something with the HTML response, for example:
                    document.body.innerHTML = html;
                })
                .catch(error => console.error('Error:', error));
            }
          } else {
              console.error('Server responded with an error:', data);
              alert("Failed to submit data: " + data.message);
          }
      })
      .catch(error => {
          console.error('Fetch error:', error);
          alert("An error occurred while submitting data.");
      });
  } catch (error) {
      console.error('Client-side error:', error);
      alert("An error occurred on the client side.");
  }
});

// Login handler
document.getElementById('loginbutton').addEventListener('click', function(event) {
    event.preventDefault();
    alert("testing")
    var email = document.getElementById('emailvalue').value;
    var password = document.getElementById('passwordvalue').value;
    console.log(email, password);
    var formData = new FormData();
    formData.append('email', email);
    formData.append('password',  password);
    fetch('/login', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            localStorage.setItem('idofregestration', data.id);
            window.location.href = '/bankDetails';
        } else {
            console.error('Server responded with an error:', data);
            alert("Failed to login: " + data.message);
        }
    }).catch(error => {
        console.error('Fetch error:', error);
        alert("An error occurred while logging in.");
    });
});