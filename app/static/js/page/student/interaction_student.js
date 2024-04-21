function action_popup(popup, card, id, obj_click) {
  if (id === "summary_route") {
    const name_line = extract_info(obj_click, "line");
    const shift = extract_info(obj_click, "turno");
    const hr_par = extract_info(obj_click, "horario_partida");
    const hr_ret = extract_info(obj_click, "horario_retorno");
    const surname = extract_info(obj_click, "apelido");
    const driver = extract_info(obj_click, "motorista");

    popup.querySelector("#summary_route_span_turno").textContent = shift;
    popup.querySelector("#summary_route_span_partida").textContent = hr_par;
    popup.querySelector("#summary_route_span_retorno").textContent = hr_ret;

    popup.querySelector("#summary_route_linha").textContent = name_line;
    popup.querySelector("#summary_route_motorista").textContent = driver;
    popup.querySelector("#summary_route_veiculo").textContent = surname;
    popup.querySelector(
      "#summary_route_horarios"
    ).textContent = `${shift} > ${hr_par} ~ ${hr_ret}`;
    load_popup_route(popup);
  } else if (id === "summary_line") {
    const name_line = extract_info(obj_click, "nome");
    document.getElementById("summary_line_nome").textContent = name_line;
    load_popup_line(card, name_line);
  } else if (id === 'edit_contraturno') {
    const contraturnos = document.getElementById('contaturnos_fixos').textContent
    const options = Array.from(document.getElementById('content_local_contraturno').children)
    options.forEach(element => {
      const text = element.querySelector('p').textContent
      if (contraturnos.includes(text.slice(0, 3)) || contraturnos === 'Todos os dias') {
        popup_confirmBox(element)
      }
    })
  }
}

function loadStops() {
  const local_diarias = document.getElementById(
    "area_agenda_diaria_local"
  );
  const local_fixas = document.getElementById("area_agenda_pontos_local");
  local_diarias.innerHTML = "";
  local_fixas.innerHTML = "";

  const loading_msg = document.getElementById("area_agenda_pontos_loading");
  loading_msg.classList.remove("inactive");

  fetch("/get_stops_student", { method: "GET" })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        loading_msg.classList.add("inactive");
        const diarias = response.data.diaria;
        const fixas = response.data.fixa;

        const model_parada = models.querySelector("#model_stop");
        if (diarias.paradas.length) {
          const container_diarias =
            document.getElementById("area_agenda_diaria");
          container_diarias.classList.remove("inactive");

          if (diarias.msg) {
            container_diarias.querySelector("span").textContent = diarias.msg;
          }
          criar_visualizacao_parada(
            model_parada,
            diarias.paradas,
            local_diarias
          );
        } else {
          document
            .getElementById("area_agenda_diaria")
            .classList.add("inactive");
        }

        if (fixas.paradas.length) {
          const span_msg = document.getElementById("area_agenda_pontos_msg");
          span_msg.innerHTML = "";

          for (msg in fixas.msg) {
            const text = document.createElement("p");
            text.className = "text secundario fundo cinza justify";
            text.textContent = fixas.msg[msg];
            span_msg.appendChild(text);
          }
          criar_visualizacao_parada(model_parada, fixas.paradas, local_fixas);
        }
      } else {
        create_popup(response.title, response.text, "Ok");
      }
    });
}

function loadWeek() {
  const container = document.getElementById('aba_agenda_scheduler')
  const local_contraturno = document.getElementById('contaturnos_fixos')
  local_contraturno.textContent = 'Carregando...'

  dias_sem = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']
  dias_sem.forEach(day => {
    container.querySelector(`#${day}_card_body`).classList.add('inactive')
    container.querySelector(`#${day}_span_load`).classList.remove('inactive')
  });

  fetch("/get_schedule_student", { method: "GET" })
  .then((response) => response.json())
  .then((response) => {
    if (!response.error) {
      const data = response.data
      local_contraturno.textContent = response.contraturno_fixo

      for (day in data) {
        const info = data[day]
        for (key in info) {
          const value = info[key]

          if (key === 'diarias') {
            if (value.length) {
              container.querySelector(`#${day}_container`).classList.remove('inactive')
              const diaria_container = document.getElementById(`${day}_area_diaria`)
              diaria_container.innerHTML = ''

              for (index in value) {
                const text = document.createElement("p");
                text.className = "text terciario content";
                text.textContent = value[index];
                diaria_container.appendChild(text);
              }
            }
          } else if (key === 'valida') {
            const card = document.getElementById(`card_${day}`)
            const icon_card_edit = document.getElementById(`card_${day}_edit`)
            const icon_card_blocked = document.getElementById(`card_${day}_blocked`)
            icon_card_edit.classList.remove('inactive')
            icon_card_blocked.classList.add('inactive')
            card.classList.remove('blocked')

            if (value) {
              card.onclick = function() {
                open_popup('edit_dia', this, false)
              }
            } else {
              card.classList.add('blocked')
              icon_card_edit.classList.add('inactive')
              icon_card_blocked.classList.remove('inactive')
            }
          } else {
            container.querySelector(`#${key}_${day}`).textContent = value
          }
        }
        container.querySelector(`#${day}_span_load`).classList.add('inactive')
        container.querySelector(`#${day}_card_body`).classList.remove('inactive')
      }
    } else {
      create_popup(response.title, response.text, "Ok");
    }
  })
}

function loadSchedule() {
  loadStops();
  loadWeek();
}

function stop_redirect(arg = false) {
  if (!arg) {
    const check_name = document
      .getElementById("area_agenda_pontos_local")
      .querySelector('[id*="linha"]');
    if (check_name) {
      closeInterface("page_user", "line", check_name.textContent.trim());
    } else {
      create_popup(
        "Não vinculado",
        "Você não possui cadastro fixo em nenhuma linha.",
        "Ok"
      );
    }
  } else {
    closeInterface("page_user", "line", arg);
  }
}
