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
window.addEventListener('resize', updateScreenSize);
localStorage.setItem('emailVerified', false);
document.getElementById('verifyemailbutton').addEventListener('click', function(event) {
 event.preventDefault();
 let emailverifysection = document.getElementById('emailverifysection');
});
document.getElementById('registrationform').addEventListener('submit', function(event) {
  event.preventDefault(); // Prevent the default form submission behavior

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
            alert(data.id)
            localStorage.setItem('idofgegestration', data.id);
            window.location.href = '/bankDetails'
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