let form = document.getElementById('form').elements;
let button = document.querySelector('.button-12');
let info = document.querySelector('.pass_info');
let e_info = document.querySelector('.mail_info');
let isPasswordValid=false;
let isPasswordConfirmValid=false;
let emailValiid = false;
form.password.addEventListener('input',(e)=>{
    let password_current = e.target.value;
    if(password_current.length>=3){
        isPasswordValid=true;
        info.innerHTML=""
    }
    else{
        isPasswordValid=false;
        info.innerHTML="Hasło mus posiadać minimum 3 znaki"
    }
})
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
    isPasswordConfirmValid=true;
    if(form.warunki.checked==true&&emailValiid&&isPasswordValid){
        document.querySelector('#register-btn').removeAttribute('disabled');
    }
}
else{
    button.disabled=true;
    info.innerHTML="Powtórzone hasło nie jest prawidłowe"
}
})

form.warunki.addEventListener('change',()=>{
    if(form.warunki.checked && isPasswordConfirmValid&&emailValiid&&isPasswordValid){
        document.querySelector('#register-btn').removeAttribute('disabled');
    }
    else{
        document.querySelector('#register-btn').setAttribute('disabled',true);
    }
})