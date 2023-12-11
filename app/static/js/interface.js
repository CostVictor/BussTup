if (window.location.href.includes('/cadastro')) {
    let divRolagem = document.querySelectorAll('form.scroll_vertical')
    const button_select = document.querySelector('button.form__btn--select_active')
    const button_submit = document.getElementById('button_submit')
    button_submit.style.marginBottom = '2.5%'

    if (button_select.textContent == 'Aluno') {
        divRolagem = divRolagem[0]
    } else {divRolagem = divRolagem[1]}

    const observer = createObserver(divRolagem)
    const elements_animate = divRolagem.querySelectorAll('div.hidden')
    elements_animate.forEach(element => {
        observer.observe(element)
    })
}

function createObserver(root, range_visibility=0.2) {
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                entry.target.classList.remove('hidden')
            } else {
                entry.target.classList.remove('visible');
                entry.target.classList.add('hidden');
            }
        });
    }, {
        root: root,
        rootMargin: '0px',
        threshold: range_visibility
    });
    return observer
}


// ~~~~~ Animações do rótulo (Label) ~~~~~ //

const inputs = document.querySelectorAll('input')
const forms = document.querySelectorAll('form')
for (let index = 0; index < forms.length; index++) {
    const div_alvo = forms[index].querySelector('div.form__container--input')
    div_alvo.style.marginTop = 0
}
inputs.forEach(input => {
    const label = document.querySelector(`label[for="${input.id}"]`)
    const icon = document.getElementById(`icon_${input.id}`)
    let inFocus = false

    function verify() {
        if (inFocus) {
            input.classList.remove('input_error')
            if (label) {label.classList.add('form__label--animate')}
            if (icon) {icon.classList.add('form__icon--animate')}
        } else {
            if (input.value.trim() === '') {
                label.classList.remove('form__label--animate')
                if (icon) {icon.classList.remove('form__icon--animate')}
            } else {
                if (label) {label.classList.add('form__label--animate')}
                if (icon) {icon.classList.add('form__icon--animate')}
            }
        }
    }
    input.addEventListener('focus', function() {inFocus = true})
    input.addEventListener('blur', function() {inFocus = false})
    setInterval(verify, 100)
})


// ~~~~~ Animação de icone ~~~~~ //

function animateIconPassword(id) {
    const iconPassword = document.getElementById(`btn_${id}`)
    const inputPassword = document.getElementById(id)

    if (inputPassword.type === 'password') {
        iconPassword.className = "bi bi-eye-slash-fill form__btn--password"
        inputPassword.type = 'text'
    } else {
        iconPassword.className = "bi bi-eye-fill form__btn--password"
        inputPassword.type = 'password'
    }
}


// ~~~~~ Animação de interface ~~~~~ //

function animate_itens(list_itens, animate='fadeDown', duraction = 0.3, dalay_init = 0, interval_itens = 0.06, opacity = 0) {
    function config_animate(index, item, name, duraction, value_initial, sum) {
        item.style.animation = `${name} ${duraction}s forwards ${value_initial + (index * sum)}s`
    }
    if (list_itens) {
        list_itens.forEach((item, index) => {
            item.style.opacity = opacity
            config_animate(index, item, animate, duraction, dalay_init, interval_itens)
        })
    }
}

function enterInterface(type) {
    if (type === 'login' || type === 'register') {
        var container = document.getElementById('container')
        var elements = container.querySelectorAll('[class*="enter"]')
    }

    if (type === 'login') {
        container.style.transition = 'border-radius 0.5s ease, height 0.85s ease 0.15s'
        container.classList.remove('container_complete')
        container.classList.add('enter--radius')
        animate_itens(elements, 'fadeDown', 0.6, 0.55)
        
    } else if (type === 'register') {
        const content = document.getElementById('content')
        content.style.marginTop = '4.5%'
        animate_itens(elements, 'fadeDown', 0.8, 0.1)
    }
}

function closeInterface(type, redirect) {
    const container = document.getElementById('container')
    let elements = container.querySelectorAll('[class*="enter"]')

    animate_itens(elements, 'outUp', 0.3, 0, 0.07, 1)
    if (type === 'login') {
        container.style.transition = 'border-radius 0.5s ease 0.4s, height 0.7s ease'
        
        setTimeout(() => {
            container.classList.remove('enter--radius')
            container.classList.add('container_complete')
        }, 300)

        setTimeout(() => {
            enterInterface('login')
            window.location.href = redirect
        }, 980)
    } else {
        setTimeout(() => {
            enterInterface('register')
            window.location.href = redirect
        }, 980)
    }
}


// ~~~~~ Troca de formulário ~~~~~ //

function replace_form(button_id) {
    const buttons = document.querySelectorAll('button.form__btn--select')
    const form_aluno = document.getElementById('form_aluno')
    const form_motorista = document.getElementById('form_motorista')
    form_aluno.scrollTop = 0
    form_motorista.scrollTop = 0

    if (button_id === 'aluno' && !buttons[0].className.includes('active')) {
        buttons[0].classList.add('form__btn--select_active')
        buttons[1].classList.remove('form__btn--select_active')
        form_aluno.classList.add('scroll_vertical')
        form_aluno.classList.remove('inative')
        form_motorista.classList.add('inative')
        form_motorista.classList.remove('scroll_vertical')

    } else if (button_id === 'motorista' && !buttons[1].className.includes('active')) {
        buttons[1].classList.add('form__btn--select_active')
        buttons[0].classList.remove('form__btn--select_active')
        form_motorista.classList.add('scroll_vertical')
        form_motorista.classList.remove('inative')
        form_aluno.classList.add('inative')
        form_aluno.classList.remove('scroll_vertical')
    }
}
