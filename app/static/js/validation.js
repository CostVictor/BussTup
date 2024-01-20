// ~~~~~ POPUP Mensagem de validação (swal2) ~~~~~ //

function create_popup(title, text='', text_buttom='Ok', icon='info', redirect='', open_scroll = true) {
    document.body.classList.add('no-scroll')
    Swal.fire({
        title: title,
        text: text,
        icon: icon,
        width: '80%',
        confirmButtonText: text_buttom,
        confirmButtonColor: '#004aad',
        iconColor: `${icon === 'info' ? "#ffe646" : icon === 'success'? "#0aa999" : "#ff7272"}`
    }).then(() => {
        if (open_scroll) {document.body.classList.remove('no-scroll')}
        if (redirect) {window.location.href = redirect}
    })
}


// ~~~~~ Validações ~~~~~ //

const inputs_tell = document.querySelectorAll('[class*="format_tell"]')
if (inputs_tell) {
    inputs_tell.forEach(input => {
        input.addEventListener('input', () => {
            let digits = input.value.replace(/\D/g, '').substring(0, 11)
            let num = digits.split('')
            
            let tell_formated = ''
            if (num.length > 0) {tell_formated += `${num.slice(0, 2).join('')}`}
            if (num.length > 2) {tell_formated = `(${tell_formated}) ${num.slice(2, 7).join('')}`}
            if (num.length > 7) {tell_formated += `-${num.slice(7).join('')}`}
            input.value = tell_formated
        })
    })
}

const inputs_name = document.querySelectorAll('[class*="format_name"]')
if (inputs_name) {
    inputs_name.forEach(input => {
        input.addEventListener('input', () => {
            input.value = input.value.replace(/[^a-zA-ZàáâãçéêíîóôõúüÀÁÂÃÇÉÊÍÎÓÔÕÚÜ\s]/g, '')
        })
    })
}


// ~~~~~ Validação ~~~~~ //

function validationLogin(event) {
    event.preventDefault()

    const form = document.getElementById('formulario_login')
    const usuario = form.elements.user.value.trim()
    const senha = form.elements.password.value.trim()

    fetch('/authenticate_user', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'user': usuario, 'password': senha})
    })
    .then(response => response.json())
    .then(response => {
        if (response['error']) {
            create_popup('Não foi possível fazer login', 'Verifique suas credenciais e tente novamente.', 'Ok', 'info')
        } else {closeInterface('login', response['redirect'])}
    })
}

function validationRegister(type, event) {
    event.preventDefault()

    const form = document.getElementById(`form_${type}`)
    let execute = true
    let data = {}

    for (let index = 0; index < form.elements.length; index++) {

    }

    if (execute) {
        fetch('/register_user', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({'table': type, 'data': data})
        })
        .then(response => response.json())
        .then(retorno => {
            let text = ''; let icon = 'success'
            let text_buttom = 'Logar'; let redirect = '/'

            if (retorno['error']) {
                icon = 'info'
                text = `Já existe um usuário cadastrado ${type === "aluno" ? "na matrícula especificada." : "no nome especificado."}`
                text_buttom = 'Voltar'
                redirect = false
            }
            create_popup(retorno['title'], text, text_buttom, icon, redirect)
        })
    } else {
        campo.classList.add('input_error')
        create_popup(erro_titulo, erro_texto, 'Voltar', 'error')
    }
}


// ~~~~~ Formulário ~~~~~ //

function submit(form_id = false) {
    if (!form_id) {
        const buttom = document.querySelector('button.form__btn--select.selected')
        var form = document.getElementById(`form_${buttom.textContent.toLowerCase()}`)
    } else {var form = document.getElementById(form_id)}
    if (form.checkValidity()) {
        form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))
    } else {form.reportValidity()}
}
