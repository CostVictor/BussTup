function register_in_point_fixed() {
  const data = return_data_route();
  const popup_point = local_popup.querySelector("#config_rel_point_route");
  data.type = extract_info(popup_point, "tipo");
  data.name_point = extract_info(popup_point, "nome");

  popup_button_load("confirm_register_in_point");
  fetch("/create_pass_fixed", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        create_popup(response.title, response.text, "Ok", "success");
        close_popup("confirm_register_in_point");
        loadInterfaceRoutes(data.name_line);
        config_popup_route(
          null,
          return_data_route(null, (format_dict_url = true))
        );
        document
          .getElementById("config_rel_point_route_cadastrar")
          .classList.add("inactive");
        document
          .getElementById("config_rel_point_route_sair")
          .classList.remove("inactive");
      } else {
        create_popup(response.title, response.text);
        popup_button_load("confirm_register_in_point", "Confirmar");
      }
    });
}

function register_in_point_contraturno() {
  const popup = local_popup.querySelector("#options_contraturno");
  const data = return_data_route();
  let execute = true;

  const option = popup.querySelector('[id*="nome"][class*="selected"]');
  if (option) {
    data.type = option.id.includes("partida") ? "partida" : "retorno";
    data.name_point = option.textContent;
  } else {
    execute = false;
  }

  if (execute) {
    popup_button_load("confirm_register_contraturno");
    fetch("/create_pass_contraturno", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
      .then((response) => response.json())
      .then((response) => {
        if (!response.error) {
          local_popup.removeChild(
            local_popup.querySelector("#options_contraturno")
          );
          close_popup("confirm_register_contraturno");
          create_popup(response.title, response.text, "Ok", "success");

          loadInterfaceRoutes(data.name_line);
          config_popup_route(
            null,
            return_data_route(null, (format_dict_url = true))
          );
        } else {
          create_popup(response.title, response.text);
          popup_button_load("confirm_register_contraturno", "Confirmar");
        }
      });
  } else {
    create_popup(
      "Nenhuma opção selecionada",
      "Selecione uma opção de ponto disponível.",
      "Voltar"
    );
  }
}

function del_myPoint_fixed() {
  const name_line = document.getElementById("interface_nome").textContent;
  const type = extract_info(
    local_popup.querySelector("#config_rel_point_route"),
    "tipo"
  );

  popup_button_load("confirm_del_mypoint");
  fetch("/del_myPoint_fixed/" + encodeURIComponent(type), { method: "DELETE" })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        document
          .getElementById("config_rel_point_route_cadastrar")
          .classList.remove("inactive");
        document
          .getElementById("config_rel_point_route_sair")
          .classList.add("inactive");

        create_popup(response.title, response.text, "Ok", "success");
        close_popup("confirm_del_mypoint");
        config_popup_route(
          null,
          return_data_route(null, (format_dict_url = true))
        );
        loadInterfaceRoutes(name_line);
      } else {
        create_popup(response.title, response.text);
        popup_button_load("confirm_del_mypoint", "Confirmar");
      }
    });
}

function del_myPoint_contraturno() {
  const name_line = document.getElementById("interface_nome").textContent;
  popup_button_load("confirm_del_mycontraturno");

  fetch("/del_myPoint_contraturno", { method: "DELETE" })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        create_popup(response.title, response.text, "Ok", "success");
        close_popup("confirm_del_mycontraturno");
        config_popup_route(
          null,
          return_data_route(null, (format_dict_url = true))
        );
        loadInterfaceRoutes(name_line);
      } else {
        create_popup(response.title, response.text);
        popup_button_load("confirm_del_mycontraturno", "Confirmar");
      }
    });
}

function agendar_diaria() {
  const option_partida = document.getElementById("sched_daily_op_partida");
  const container_partida = document.getElementById(
    "sched_daily_op_partida_container"
  );

  const option_retorno = document.getElementById("sched_daily_op_retorno");
  const container_retorno = document.getElementById(
    "sched_daily_op_retorno_container"
  );

  let execute = true;
  const title = "Nenhuma opção selecionada";
  let text =
    "Você precisa selecionar pelo menos uma opção de trajeto para agendar uma diária.";
  const data = return_data_route(null);
  data.date = document.getElementById("sched_daily_date").value.trim();

  if (
    !return_bool_selected(option_partida) &&
    !return_bool_selected(option_retorno)
  ) {
    execute = false;
  }

  if (return_bool_selected(option_partida)) {
    let selected_partida = return_option_selected(container_partida);
    if (!selected_partida) {
      text = "Você não selecionou uma opção de partida.";
      execute = false;
    } else {
      selected_partida = selected_partida.split(" - ");
      data.partida = selected_partida[selected_partida.length - 1];
    }
  }

  if (return_bool_selected(option_retorno)) {
    let selected_retorno = return_option_selected(container_retorno);
    if (!selected_retorno) {
      text = "Você não selecionou uma opção de retorno.";
      execute = false;
    } else {
      selected_retorno = selected_retorno.split(" - ");
      data.retorno = selected_retorno[selected_retorno.length - 1];
    }
  }

  if (execute) {
    popup_button_load("sched_daily");
    fetch("/create_pass_daily", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
      .then((response) => response.json())
      .then((response) => {
        if (!response.error) {
          create_popup(response.title, response.text, "Ok", "success");
          close_popup("sched_daily");
          config_popup_route(
            null,
            return_data_route(null, (format_dict_url = true))
          );
          loadInterfaceRoutes(data.name_line);
        } else {
          popup_button_load("sched_daily", "Agendar");
          create_popup(response.title, response.text);
        }
      });
  } else [create_popup(title, text)];
}

function deletar_diaria() {
  const data = return_data_route(null);
  data.type = document.getElementById("confirm_del_daily_type").textContent;
  data.name_point = document.getElementById(
    "confirm_del_daily_name_point"
  ).textContent;
  data.date = document.getElementById("confirm_del_daily_date").textContent;

  popup_button_load("confirm_del_daily");
  fetch("/del_pass_daily", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        create_popup(response.title, response.text, "Ok", "success");
        close_popup("confirm_del_daily");
        config_popup_route(
          null,
          return_data_route(null, (format_dict_url = true))
        );
        loadInterfaceRoutes(data.name_line);
      } else {
        create_popup(response.title, response.text);
        popup_button_load("confirm_del_daily", "Confirmar");
      }
    });
}
