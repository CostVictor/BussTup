function enterPerfil() {
    const perfil = document.querySelector('section.perfil__container')
    const header = perfil.querySelector('header')
    header.classList.remove('enter')

    const elements = document.querySelectorAll('[class*="enter"]')
    config_animate(0, header, 'fadeDown', 0.5, 0, 0.06)
    animate_itens(elements, 'fadeDown', 0.5, 0.2)
}


function closePerfil(logout = false) {
    const perfil = document.querySelector('section.perfil__container')
    const header = perfil.querySelector('header')
    header.classList.add('enter')

    const elements = document.querySelectorAll('[class*="enter"]')
    animate_itens(elements, 'outUp', 0.5, 0, 0.03, 1)

    if (logout) {

    } else {
        setTimeout(() => {
            window.location.href = "/pagina-usuario"
        }, 1000)
    }
    setTimeout(() => {enterPerfil()}, 1100)
}
