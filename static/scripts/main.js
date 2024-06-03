let form = document.getElementById('form').elements;
let button = document.querySelector('.button-12');
let info = document.querySelector('.pass_info');
let e_info = document.querySelector('.mail_info');
let passwordValid=false;
let emailValiid = false;
form.email.addEventListener('input',(e)=>{
    let mail = e.target.value;
    if(mail.includes('@')){
        let afterSplit = mail.split('@');
        if(afterSplit[1].includes('.')){
            if(afterSplit[1].split('.')[1]!='')
            emailValiid=true;
            info.innerHTML='';
        }
        else{
            emailValiid=false;
            info.innerHTML='Adres email jest nieprawidłowy';
        }
    }
    else{
        emailValiid=false;
    }
})
form.password_confirm.addEventListener('input',(e)=>{
let pass = form.password.value;
if(e.target.value==pass){
    confirm_pass=e.target.value;
    info.innerHTML="";
    passwordValid=true;
    if(form.warunki.checked==true&&emailValiid){
        document.querySelector('#register-btn').removeAttribute('disabled');
    }
}
else{
    button.disabled=true;
    info.innerHTML="Powtórzone hasło nie jest prawidłowe"
}
})
form.warunki.addEventListener('change',()=>{
    if(form.warunki.checked && passwordValid&&emailValiid){
        document.querySelector('#register-btn').removeAttribute('disabled');
    }
    else{
        document.querySelector('#register-btn').setAttribute('disabled',true);
    }
})