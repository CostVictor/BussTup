// ~~~~~ POPUP Mensagem de validação (swal2) ~~~~~ //

function create_popup(title, text='', text_buttom='Ok', icon='info', redirect='', open_scroll = true) {
    document.body.classList.add('no-scroll')
    Swal.fire({
        title: title,
        html: `<p${text.split(' ').length > 12 ? ' style="text-align: justify;"' : ''}>${text}</p>`,
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


// ~~~~~ Validações de input ~~~~~ //

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


const inputs_options = document.querySelectorAll('[class*="format_options"]')
if (inputs_options) {
    function ajust_text(list, input) {
        const value = input.value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
        list.forEach(element => {
            const text = element.textContent.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
            element.classList.toggle('inactive', !text.includes(value));
        })
    }

    inputs_options.forEach(input => {
        const list_options = input.parentNode.parentNode.querySelector('ul')
        const elements = list_options.querySelectorAll('li')
        animate_itens(elements)

        elements.forEach(li => {
            li.addEventListener('mouseenter', () => {
                input.value = li.textContent
            })
        })

        input.addEventListener('input', () => {
            ajust_text(elements, input)
        })

        input.addEventListener('focus', () => {
            input.classList.add('option_focus')
            list_options.classList.remove('inactive')
            list_options.scrollTop = 0
            ajust_text(elements, input)
        })

        input.addEventListener('blur', () => {
            input.classList.remove('option_focus')
            list_options.classList.add('inactive')

            elements.forEach(element => {
                element.classList.remove('inactive')
            })
        })
    })
}


// ~~~~~ Validação Geral ~~~~~ //

function check_policy_password(password) {
    let msg = 'A senha deve possuir pelo menos'
    let list_exi = []

    let caractere_maisculo = /[A-Z]/.test(password)
    if (!caractere_maisculo) {
        list_exi.push('1 (um) caractere em maiúsculo')
    }
    
    let caractere_numero = /\d/.test(password)
    if (!caractere_numero) {
        list_exi.push('1 (um) caractere número')
    }

    let caractere_simbolo = /[!@#$%^&*()_+{}\[\]:;<>,.?~\\/-]/.test(password)
    if (!caractere_simbolo) {
        list_exi.push('1 (um) caractere símbolo')
    } 

    if (list_exi.length) {
        return `${msg} ${list_exi.join(', ')}.`
    }
    return false
}


function validationLogin(event) {
    event.preventDefault()

    const form = document.getElementById('formulario_login')
    const usuario = form.elements.user.value.trim()
    const senha = form.elements.password.value.trim()

    fetch('/authenticate_user', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'login': usuario, 'password': senha})
    })
    .then(response => response.json())
    .then(response => {
        if (response['error']) {
            create_popup(response['title'], response['text'], 'Ok', 'info')
        } else {closeInterface('login', response['redirect'])}
    })
}

function validationRegister(form_submit, event) {
    event.preventDefault()
    
    let execute = true
    let data = {}

    const list_input = form_submit.querySelectorAll('input')
    for (let index = 0; index < list_input.length; index++) {
        var input = list_input[index]

        if (input.name === 'password') {
            var check = check_policy_password(input.value.trim())
            if (check) {
                execute = false
                var erro_title = 'Senha inválida'
                var erro_text = check
                break
            }
        }
        
        if (input.name === 'password_conf') {
            if (input.value.trim() !== data['password']) {
                execute = false
                var erro_title = 'Falha de confirmação'
                var erro_text = 'A senha especificada na confirmação é diferente da senha definida.'
                break
            }
        } else {data[input.name] = input.value.trim()}
    }

    if (execute) {
        fetch('/register_user', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({'data': data})
        })
        .then(response => response.json())
        .then(retorno => {
            if (retorno['error']) {
                create_popup(retorno['title'], retorno['text'], 'Voltar', 'info')
            } else {
                create_popup(retorno['title'], retorno['text'], 'Acessar login', 'success', '/') 
            }
        })
    } else {
        input.classList.add('input_error')
        create_popup(erro_title, erro_text, 'Voltar', 'error')
    }
}


// ~~~~~ Formulário ~~~~~ //

function submit(form_id = false) {
    if (!form_id) {
        const buttom = document.querySelector('button.form__btn--select.selected')
        var form = document.getElementById(`form_${buttom.textContent.toLowerCase()}`)
    } else {var form = document.getElementById(form_id)}

    let execute = true
    const inputs = form.querySelectorAll('input')
    inputs.forEach(input => {
        if (input.type === 'submit') {
            execute = false
        }
    })

    if (execute) {
        if (form.checkValidity()) {
            form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))
        } else {form.reportValidity()}
    }
}
