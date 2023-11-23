window.sr = ScrollReveal({ reset: true })

function enterPage() {
    const header = document.getElementById('header')
    const content = document.getElementById('content')
    const nav = document.getElementById('nav')

    content.classList.remove('content_noBorder')
    setTimeout(() => {
        header.classList.remove('header_hidden')
    }, 180)
    setTimeout(() => {
        sr.reveal('.page__container--header', { duration: 600 })
        nav.classList.remove('nav_hidden')
    }, 500)
}
