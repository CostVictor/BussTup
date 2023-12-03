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
        setInterval(request_data, 3000)
        
        socket.on('return_lines', (data) => {
            console.log(data)
        })

        socket.on('return_schedule', (data) => {
            console.log(data)
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
    setTimeout(() => {
        elements.forEach((element, index) => {
            element.style.opacity = 0
            animated(index, element, 'fadeDown', 0.7, 0)
        })
    }, 600)
}

function closePage() {}

function open_popup_edit(id) {
    document.body.classList.add('no-scroll')
    const popup = document.getElementById(id)
    const card = popup.querySelector('div.popup__container')
    popup.classList.remove('inative')
    popup.classList.remove('close')
    card.classList.remove('close')
}

function cancel_popup_edit(id) {
    const popup = document.getElementById(id)
    const card = popup.querySelector('div.popup__container')
    card.classList.add('close')
    popup.classList.add('close')
    setTimeout(() => {
        popup.classList.add('inative')
        document.body.classList.remove('no-scroll')
    }, 100)
}


// ~~ Animação de rolamento ~~ //

function ajustAba(index_atual) {
    const abas = document.querySelectorAll('div.page__container.column')
    abas.forEach((aba, index_aba) => {
        if (index_aba === index_atual) {
            aba.classList.remove('inative')
        } else {
            aba.classList.add('inative')
        }
    })
}

let isScrolling
content.addEventListener('scroll', function() {
    clearTimeout(isScrolling)
    isScrolling = setTimeout(function() {
        const larguraDiv = content.scrollWidth / divs.length;
        const index = Math.floor(content.scrollLeft / larguraDiv)
      
        btns.forEach((btn) => {
            btn.classList.remove('btn_selected')
        })
        btns[index].classList.add('btn_selected')
        ajustAba(index)
    }, 40)
  })

function replaceAba(btn_id) {
    let index_atual = 0
    btns.forEach((element, index) => {
        if (element.id === btn_id) {
            const divAlvo = divs[index]
            content.scrollLeft = divAlvo.offsetLeft
            element.classList.add('btn_selected')
            aba_atual = element.id
            index_atual = index
        } else {
            element.classList.remove('btn_selected')
        }
    })
    ajustAba(index_atual)
}

const rolagens = document.querySelectorAll('div.scroll_horizontal')
for (let index = 0; index < rolagens.length; index++) {
    const observer = createObserver(rolagens[index], 0.15)
    let elements_animate = rolagens[index]
    elements_animate = elements_animate.querySelectorAll('div.hidden')
    elements_animate.forEach(element => {
        observer.observe(element)
    })
}


// ~~ Interações na aba ~~ //

// ~~ Aba agenda
function checkForecast(pos) {
    const btn_title = document.getElementById(`title_${pos}`)
    const icon_title = btn_title.querySelector('i')
    const container_dias = document.getElementById(`dias_${pos}`)
    dias = container_dias.querySelectorAll('div.align')
    
    if (container_dias.className.includes('inative')) {
        dias.forEach((item, index) => {
            item.style.opacity = 0
            animated(index, item, 'fadeDown', 0.3, 0)
        })
        container_dias.classList.remove('inative')
        icon_title.classList.add('open')
    } else {
        container_dias.classList.add('inative')
        icon_title.classList.remove('open')
    }
}
