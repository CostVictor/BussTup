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
  }
}

function load_popup_migrate(name_line, surname) {
  const container = document.getElementById("migrate_capacity_container");
  const data = {
    principal: [name_line],
    secondary: { surname_ignore: surname, only_valid: true },
  };
  include_options_container(
    container,
    "option_vehicle",
    data,
    false,
    false,
    "model_option_box",
    true
  );
}
