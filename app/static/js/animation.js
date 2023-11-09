// ~~~~~ Animações do rótulo (Label) ~~~~~ //

function focusLabel(id) {
    const label = document.querySelector(`label[for=${id}]`)
    const input = document.getElementById(id)

    label.classList.add('form__label--animate')
    input.classList.remove('form__box_input--error')
}

function blurLabel(id) {
    const input = document.getElementById(id)
    const label = document.querySelector(`label[for=${id}]`)

    if (input.value === '') {
        label.classList.remove('form__label--animate')
        input.value = ''
    }
}

// ~~~~~ Animação de icone ~~~~~ //

function animateIconPassword(id) {
    const iconPassword = document.getElementById(`icon_${id}`)
    const inputPassword = document.getElementById(id)

    if (inputPassword.type === 'password') {
        iconPassword.className = "bi bi-eye-slash-fill form__icon_password"
        inputPassword.type = 'text'
    } else {
        inputPassword.type = 'password'
        iconPassword.className = "bi bi-eye-fill form__icon_password"
        iconPassword.classList.add('bi-eye-fill')
        iconPassword.classList.remove('bi-eye')
    }
}

// ~~~~~ Animação de transição de interface ~~~~~ //

function replaceForm (type) {
    const buttonAluno = document.getElementById('button_aluno')
    const buttonMotorista = document.getElementById('button_motorista')
    const formAluno = document.getElementById('form_register_aluno')
    const formMotorista = document.getElementById('form_register_motorista')

    if (type === 'aluno') {
        buttonAluno.classList.add('form__btn_option--focus')
        buttonMotorista.classList.remove('form__btn_option--focus')

        formAluno.classList.add('ative')
        formAluno.classList.remove('inative')
        formMotorista.classList.remove('ative')
        formMotorista.classList.add('inative')

    } else {
        buttonMotorista.classList.add('form__btn_option--focus')
        buttonAluno.classList.remove('form__btn_option--focus')

        formMotorista.classList.add('ative')
        formMotorista.classList.remove('inative')
        formAluno.classList.remove('ative')
        formAluno.classList.add('inative')

        console.log(formMotorista.className)
    }
}

function enterInterfaceForm(type) {
    function comparar(elementoPai, elementoFilho) {
        let heightPai = elementoPai.clientHeight
        let heightFilho = elementoFilho.clientHeight

        if (heightFilho > heightPai) {return heightFilho}
        return false
    }

    const sectionImg = document.querySelector('section.img_container')
    const sectionForm = document.querySelector('section.form_container')

    if (sectionForm) {
        const form = sectionForm.querySelector('form')
        let comp = comparar(sectionForm, form)

        if (comp) {sectionForm.style.height = `${comp}px`}
        sectionForm.classList.add('enter_opacity')
    }

    if (type === 'login') {
        const imgLogo = sectionImg.querySelector('img#img_logo')

        sectionImg.classList.remove('recuo_50')
        imgLogo.classList.add('enter_opacity')
    } else {
        const textLogo = sectionImg.querySelector('h1')

        sectionImg.classList.add('recuo_50')
        textLogo.classList.add('enter_opacity')
        sectionForm.style.marginTop = '5%'
        sectionImg.style.marginBottom = '-34%'
        replaceForm('aluno')
    }
};
