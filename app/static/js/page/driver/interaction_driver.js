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
  } else if (id === "notice_migrate") {
    const span_type = document.getElementById("notice_migrate_type");
    const span_date = document.getElementById("notice_migrate_date");
    const btn_action = document.getElementById('notice_migrate_action')

    if (obj_click.id.includes("summary_route")) {
      let type = obj_click.id.split("_");
      type = type[type.length - 2];
      span_type.textContent = type.trim();

      let date = document
        .getElementById("summary_route_dia_previsao")
        .textContent.split(" ");
      date = date[date.length - 1];
      span_date.textContent = date;
    } else if (obj_click.id.includes("forecast_route")) {
      const info = obj_click.id.split("_");
      span_type.textContent = info[info.length - 1];
      span_date.textContent = document.getElementById(
        `forecast_route_${info[info.length - 2]}_date`
      ).textContent;
    }
    btn_action.onclick = function() {
      create_migrate_crowded('page')
    }
  }
}

function loadSchedule() {
  const load_span = document.getElementById("rotas_lotadas_span_load");
  load_span.classList.remove('inactive')
  const container_lotacao = document.getElementById("rotas_lotadas_container");
  container_lotacao.innerHTML = "";

  fetch("/get_crowded", { method: "GET" })
  .then((response) => response.json())
  .then((response) => {
    load_span.classList.add('inactive')
    const text = document.createElement("p");
    text.className =
      "text secundario fundo cinza justify";
    container_lotacao.appendChild(text);

    if (!response.error) {
      const data = response.data
      if (data.length) {
        text.classList.remove('cinza')
        text.classList.add('margin_bottom')
        text.style.width = 'fit-content'

        if (data.length > 1) {
          text.textContent = 'Identificado nas rotas:';
        } else {
          text.textContent = 'Identificado na rota:';
        }
        create_routes(data, container_lotacao, false, false, false, false);
      } else {
        text.textContent = 'Nenhuma lotação identificada';
      }
    } else {
      create_popup(response.title, response.text);
      const text = document.createElement("p");
      text.className =
        "text secundario fundo cinza justify -enter-";
      text.textContent = 'Recarregue a página e tente novamente';
      container_lotacao.appendChild(text);
    }
  })
}
