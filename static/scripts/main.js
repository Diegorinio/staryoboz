let form = document.getElementById('form').elements;
let button = document.querySelector('.button-12');
let info = document.querySelector('.pass_info');
// button.enabled = true
console.log('test')
form.password_confirm.addEventListener('input',(e)=>{
console.log(e.target.value);
let pass = form.password.value;
if(e.target.value==pass){
    button.disabled=false;
    info.innerHTML="";
}
else{
    button.disabled=true;
    info.innerHTML="Powtórzone hasło nie jest prawidłowe"
}
})
form.warunki.addEventListener('change',()=>{
    console.log(form.warunki.checked);
    console.log(document.querySelector('#register-btn').getAttribute('disabled'));
    if(form.warunki.checked){
        document.querySelector('#register-btn').removeAttribute('disabled');
    }
    else{
        document.querySelector('#register-btn').setAttribute('disabled',true);
    }
})