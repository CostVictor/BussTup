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
  } else if (id === "edit_contraturno") {
    const contraturnos =
      document.getElementById("contaturnos_fixos").textContent;
    const options = Array.from(
      document.getElementById("content_local_contraturno").children
    );
    options.forEach((element) => {
      const text = element.querySelector("p").textContent;
      if (
        contraturnos.includes(text.slice(0, 3)) ||
        contraturnos === "Todos os dias"
      ) {
        popup_confirmBox(element);
      }
    });
  } else if (id === "edit_dia") {
    const day = obj_click.id.split("_")[1];
    const faltara = obj_click.querySelector(`#faltara_${day}`).textContent;
    const contraturno = obj_click.querySelector(
      `#contraturno_${day}`
    ).textContent;

    popup.querySelector("#dia").textContent = day;
    popup.querySelector("#data_dia").textContent = obj_click.querySelector(
      `#data_${day}`
    ).textContent;
    set_selected_bool(popup.querySelector("#options_falta"), faltara);
    set_selected_bool(popup.querySelector("#options_contraturno"), contraturno);

    config_popup_day();
  }
}

function loadStops() {
  const local_diarias = document.getElementById("area_agenda_diaria_local");
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
  const container = document.getElementById("aba_agenda_scheduler");
  const local_contraturno = document.getElementById("contaturnos_fixos");
  local_contraturno.textContent = "Carregando...";

  dias_sem = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"];
  dias_sem.forEach((day) => {
    container.querySelector(`#${day}_card_body`).classList.add("inactive");
    container.querySelector(`#${day}_span_load`).classList.remove("inactive");
  });

  fetch("/get_schedule_student", { method: "GET" })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        const data = response.data;
        local_contraturno.textContent = response.contraturno_fixo;

        for (day in data) {
          const info = data[day];
          for (key in info) {
            const value = info[key];

            if (key === "diarias") {
              if (value.length) {
                container
                  .querySelector(`#${day}_container`)
                  .classList.remove("inactive");
                const diaria_container = document.getElementById(
                  `${day}_area_diaria`
                );
                diaria_container.innerHTML = "";

                for (index in value) {
                  const text = document.createElement("p");
                  text.className = "text terciario content";
                  text.textContent = value[index];
                  diaria_container.appendChild(text);
                }
              }
            } else if (key === "valida") {
              const card = document.getElementById(`card_${day}`);
              const icon_card_edit = document.getElementById(
                `card_${day}_edit`
              );
              const icon_card_blocked = document.getElementById(
                `card_${day}_blocked`
              );
              const card_content = document.getElementById(
                `${day}_card_content`
              );
              const span_info = document.getElementById(`${day}_span_info`);

              icon_card_edit.classList.remove("inactive");
              icon_card_blocked.classList.add("inactive");
              card.classList.remove("blocked");

              if (value) {
                card_content.classList.remove("inactive");
                span_info.classList.add("inactive");

                card.onclick = function () {
                  open_popup("edit_dia", this, false);
                };
              } else {
                card.classList.add("blocked");
                icon_card_edit.classList.add("inactive");
                icon_card_blocked.classList.remove("inactive");

                card_content.classList.add("inactive");
                span_info.classList.remove("inactive");
                span_info.textContent = info["info"]
              }
            } else if (key.includes("content")) {
              const new_key = key.split("_");
              if (value) {
                container
                  .querySelector(`#${new_key[new_key.length - 1]}_${day}`)
                  .classList.add("content");
              } else {
                container
                  .querySelector(`#${new_key[new_key.length - 1]}_${day}`)
                  .classList.remove("content");
              }
            } else if (key !== "info") {
              container.querySelector(`#${key}_${day}`).textContent = value;
            }
          }
          container
            .querySelector(`#${day}_span_load`)
            .classList.add("inactive");
          container
            .querySelector(`#${day}_card_body`)
            .classList.remove("inactive");
        }
      } else {
        create_popup(response.title, response.text, "Ok");
      }
    });
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

function config_popup_day() {
  const day = document.getElementById("dia").textContent;
  const diarias_card = Array.from(
    document.getElementById(`${day}_area_diaria`).children
  );

  const container = document.getElementById("edit_dia_msg");
  const span_msg = container.querySelector("span");
  container.classList.add("inactive");
  span_msg.innerHTML = "";

  const icon_blocked_faltara = document.getElementById(
    "edit_dia_faltara_blocked"
  );
  const icon_blocked_contraturno = document.getElementById(
    "edit_dia_contraturno_blocked"
  );
  const optios_faltara = document.getElementById("options_falta");
  const optios_contraturno = document.getElementById("options_contraturno");

  let blocked_faltara = false;
  let blocked_contraturno = false;

  if (diarias_card.length) {
    container.classList.remove("inactive");
    diarias_card.forEach((element) => {
      const text = document.createElement("p");
      text.className = "text secundario fundo justify";
      span_msg.appendChild(text);

      if (element.id.includes("partida")) {
        set_selected_bool(optios_faltara, "Sim");
        set_selected_bool(optios_contraturno, "Não");
        text.textContent =
          "Você possui uma diária do tipo partida marcada para este dia.";
        blocked_faltara = true;
        blocked_contraturno = true;
      } else {
        set_selected_bool(optios_contraturno, "Não");
        text.textContent =
          "Você possui uma diária do tipo retorno marcada para este dia.";
        blocked_contraturno = true;
      }
    });
  }

  const p_faltara = document.getElementById(`faltara_${day}`);
  const p_contraturno = document.getElementById(`contraturno_${day}`);
  if (!p_faltara.className.includes("content")) {
    container.classList.remove("inactive");
    blocked_faltara = true;
    const text = document.createElement("p");
    text.className = "text secundario fundo justify";
    text.textContent =
      "A opção de falta foi bloqueada pois o horário limite de alteração foi atingido.";
    span_msg.appendChild(text);
  }

  if (!p_contraturno.className.includes("content")) {
    container.classList.remove("inactive");
    blocked_contraturno = true;
    const text = document.createElement("p");
    text.className = "text secundario fundo justify";
    text.textContent =
      "A opção de contraturno foi bloqueada pois o horário limite de alteração foi atingido.";
    span_msg.appendChild(text);
  }

  if (blocked_faltara) {
    icon_blocked_faltara.classList.remove("inactive");
    Array.from(optios_faltara.children).forEach((element) => {
      element.classList.add("blocked");
    });
  } else {
    icon_blocked_faltara.classList.add("inactive");
    Array.from(optios_faltara.children).forEach((element) => {
      element.classList.remove("blocked");
      element.onclick = function () {
        popup_selectOption(this);
        config_popup_day();
      };
    });
  }

  const state_faltara = return_bool_selected(optios_faltara);
  if (blocked_contraturno || state_faltara) {
    icon_blocked_contraturno.classList.remove("inactive");
    Array.from(optios_contraturno.children).forEach((element) => {
      element.classList.add("blocked");
    });
    if (state_faltara) {
      set_selected_bool(optios_contraturno, "Não");
    }
  } else {
    icon_blocked_contraturno.classList.add("inactive");
    Array.from(optios_contraturno.children).forEach((element) => {
      element.classList.remove("blocked");
      element.onclick = function () {
        popup_selectOption(this);
        config_popup_day();
      };
    });
  }
}
