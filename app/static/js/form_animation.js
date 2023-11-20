if (window.location.href.includes('/cadastro')) {
    let divRolagem = document.querySelectorAll('form.scroll_vertical')
    const button_select = document.querySelector('button.form__btn--select_active')
    const button_submit = document.getElementById('button_submit')
    button_submit.style.marginBottom = '2.5%'

    if (button_select.textContent == 'Aluno') {
        divRolagem = divRolagem[0]
    } else {divRolagem = divRolagem[1]}

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
        root: divRolagem,
        rootMargin: '0px',
        threshold: 0.2
      });

    const elements_animate = divRolagem.querySelectorAll('div.hidden')
    elements_animate.forEach(element => {
        observer.observe(element)
    })
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

    input.addEventListener('blur', function() {
        if (input.value === '') {
            label.classList.remove('form__label--animate')
            icon.classList.remove('form__icon--animate')
            input.value = ''
        }
    })
})

function focusLabel(id) {
    const label = document.querySelector(`label[for="${id}"]`)
    const icon = document.getElementById(`icon_${id}`)
    const input = document.getElementById(id)

    label.classList.add('form__label--animate')
    icon.classList.add('form__icon--animate')
    input.classList.remove('form__box_input--error')
}

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

function animated(index, item, name, duraction = 0.5, value_initial = 0.55, sum = 0.06) {
    item.style.animation = `${name} ${duraction}s forwards ${value_initial + (index * sum)}s`
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
        elements.forEach((element, index) => {
            element.style.opacity = 0
            animated(index, element, 'fadeDown')
        })
    } else if (type === 'register') {
        const content = document.getElementById('content')
        content.style.marginTop = '5%'
        elements.forEach((element, index) => {
            element.style.opacity = 0
            animated(index, element, 'fadeDown', 0.8, 0)
        })
    }
}

function closeInterface(type, redirect) {
    const container = document.getElementById('container')
    let elements = container.querySelectorAll('[class*="enter"]')

    elements.forEach((element, index) => {
        element.style.opacity = 1
        animated(index, element, 'outUp', duraction= 0.3, value_initial = 0)
    })

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
