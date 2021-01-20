// Copy to Clipboard
function copyClipboard() {

  var copyText = document.getElementById("RefCode");

  /* Select the text field */
  copyText.select();

  /* Copy the text inside the text field */
  document.execCommand("copy");

  /* Alert the copied text */
  alert("Votre code a bien été copié 😀 !");
}

// Success SMS Sent
function successSms() {
  /* Alert the copied text */
  alert("Votre SMS a bien été envoyé 😀 !");
}

// Success Email Sent
function successEmail() {
    /* Alert the copied text */
    alert("Votre email a bien été envoyé 😀 !");
}