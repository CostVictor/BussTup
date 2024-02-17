function replace_form(obj_button) {
    function reset_form(form) {
        form.querySelectorAll('input').forEach(input => {
            input.value = ''
        })
    }
    const buttons = document.querySelectorAll('button.form__btn--select')
    const form_aluno = document.getElementById('form_aluno')
    const form_motorista = document.getElementById('form_motorista')

    const elements_aluno = Array.from(form_aluno.children)
    const elements_motorista = Array.from(form_motorista.children)

    if (obj_button.textContent === 'Aluno' && !buttons[0].className.includes('selected')) {
        buttons[0].classList.add('selected')
        buttons[1].classList.remove('selected')
        form_aluno.classList.add('scroll_vertical')
        form_aluno.classList.remove('inactive')
        form_motorista.classList.add('inactive')
        form_motorista.classList.remove('scroll_vertical')

        reset_form(form_aluno)
        animate_itens(elements_aluno, 'fadeDown', 0.6, 0, 0.07)
        form_aluno.removeAttribute('style')
        form_aluno.classList.remove('-enter-')
        form_aluno.scrollTop = 0

    } else if (obj_button.textContent === 'Motorista' && !buttons[1].className.includes('selected')) {
        buttons[1].classList.add('selected')
        buttons[0].classList.remove('selected')
        form_motorista.classList.add('scroll_vertical')
        form_motorista.classList.remove('inactive')
        form_aluno.classList.add('inactive')
        form_aluno.classList.remove('scroll_vertical')

        reset_form(form_motorista)
        animate_itens(elements_motorista, 'fadeDown', 0.6, 0, 0.07)
        form_motorista.scrollTop = 0
    }
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
            if (input.value.trim() !== data.password) {
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
            if (retorno.error) {
                create_popup(retorno.title, retorno.text, 'Voltar')
            } else {
                create_popup(retorno.title, retorno.text, 'Acessar login', 'success', 'login') 
            }
        })
    } else {
        input.classList.add('input_error')
        create_popup(erro_title, erro_text, 'Voltar', 'error')
    }
}


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
