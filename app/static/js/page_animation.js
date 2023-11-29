window.sr = ScrollReveal({ reset: true })

const header = document.getElementById('header')
const content = document.getElementById('content')
const nav = document.getElementById('nav')

const divs = content.querySelectorAll('div.page__container--aba')
const btns = nav.querySelectorAll('i.page__icon--btn')
let aba_atual = nav.querySelector('i.btn_selected').id

// ~~ Web Socket ~~ //

fetch('/gerar_token', {method: 'GET'})
.then(response => response.json())
.then(response => {
    const token = response['token_access']
    const socket = io.connect('http://localhost:5000', {secure: true})
    
    socket.on('connect', () => {
        function request_data() {
            switch (aba_atual) {
                case 'agenda': break
                case 'ponto': break
                case 'linha': break
                case 'chat': break
            }
        }
        socket.emit('send_schedule', { token })
        let aba_ant = aba_atual
    
        setInterval(() => {
            if (aba_ant !== aba_atual) {
                aba_ant = aba_atual
                request_data()
            }
        }, 500)
        setInterval(request_data, 5000)
        
        socket.on('return_lines', (data) => {
            console.log(data)
        })

        socket.on('return_schedule', (data) => {
            const area_agenda = document.getElementById('area_agenda')
        })
    })
})

// ~~ Animação de página ~~ //

function enterPage() {
    content.classList.remove('content_noBorder')
    setTimeout(() => {
        header.classList.remove('header_hidden')
    }, 180)
    setTimeout(() => {
        sr.reveal('.page__container--header', { duration: 600 })
        nav.classList.remove('nav_hidden')
    }, 500)
    var elements = document.querySelectorAll('[class*="enter"]')
    elements.forEach((element, index) => {
        element.style.opacity = 0
        animated(index, element, 'fadeDown', 0.8, 0.6)
    })
}

// ~~ Animação de rolamento ~~ //

let isScrolling
content.addEventListener('scroll', function() {
    clearTimeout(isScrolling)
    isScrolling = setTimeout(function() {
        const larguraDiv = content.scrollWidth / divs.length;
        const index = Math.floor(content.scrollLeft / larguraDiv)
        const abas = document.querySelectorAll('div.page__container--aba')
      
        btns.forEach((btn) => {
            btn.classList.remove('btn_selected')
        })
        btns[index].classList.add('btn_selected')
    }, 40)
  })

function replaceAba(btn_id) {
    const abas = document.querySelectorAll('div.page__container--aba')
    btns.forEach((element, index) => {
        if (element.id === btn_id) {
            const divAlvo = divs[index]
            content.scrollLeft = divAlvo.offsetLeft
            element.classList.add('btn_selected')
            aba_atual = element.id
            // abas[index].style.display = 'flex'
        } else {
            element.classList.remove('btn_selected')
            // abas[index].style.display = 'none'
        }
    })
}

const rolagens = document.querySelectorAll('div.scroll_horizontal')
for (let index = 0; index < rolagens.length; index++) {
    const observer = createObserver(rolagens[index])
    let elements_animate = rolagens[index]
    elements_animate = elements_animate.querySelectorAll('div.hidden')
    elements_animate.forEach(element => {
        observer.observe(element)
    })
}
