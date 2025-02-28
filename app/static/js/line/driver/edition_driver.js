function create_vehicle() {
  const name_line = document.getElementById("interface_nome").textContent;
  const surname = document.getElementById("add_vehicle_surname").value;
  const capacidade = document.getElementById("add_vehicle_capacidade").value;
  const cor = document.getElementById("add_vehicle_cor").value;
  const modelo = document.getElementById("add_vehicle_modelo").value;
  const descricao = document.getElementById("add_vehicle_descricao").value;
  const options = return_bool_selected(
    document.getElementById("add_vehicle_options")
  );

  let execute = true;
  let motorista_selected = "Nenhum";
  if (options) {
    const container = document.getElementById("add_vehicle_options_container");
    motorista_selected = return_option_selected(container);

    if (!motorista_selected) {
      execute = false;
      var title = "Nenhuma opção selecionada";
      var text = "Selecione uma opção de motorista disponível.";
    }
  }

  if (execute) {
    popup_button_load("add_vehicle");

    fetch("/create_vehicle", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        apelido: surname,
        capacidade: capacidade,
        cor: cor,
        modelo: modelo,
        descricao: descricao,
        motorista_nome: motorista_selected,
        name_line: name_line,
      }),
    })
      .then((response) => response.json())
      .then((response) => {
        if (!response.error) {
          close_popup("add_vehicle");
          create_popup(response.title, response.text, "Ok", "success");
          loadInterfaceVehicle(name_line);
        } else {
          create_popup(response.title, response.text, "Voltar");
          popup_button_load("add_vehicle", "Adicionar");
        }
      });
  } else {
    create_popup(title, text, "Voltar");
  }
}

function create_point(event) {
  event.preventDefault();

  const name_line = document.getElementById("interface_nome").textContent;
  const name_point = document.getElementById("add_point_nome").value.trim();
  const tolerance_point = document
    .getElementById("add_point_tolerancia")
    .value.trim();
  const gps_point = document.getElementById("add_point_gps").value.trim();

  let data = {
    name_point: name_point,
    tempo_tolerancia: tolerance_point,
    linkGPS: gps_point,
    name_line: name_line,
  };
  if (!gps_point) {
    delete data.linkGPS;
  }
  if (!tolerance_point) {
    delete data.tempo_tolerancia;
  }

  popup_button_load("add_point");
  fetch("/create_point", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        close_popup("add_point");
        create_popup(response.title, response.text, "Ok", "success");
        loadInterfacePoints(name_line);
      } else {
        create_popup(response.title, response.text, "Voltar");
        popup_button_load("add_point", "Criar");
      }
    });
}

function create_route(event) {
  event.preventDefault();

  const name_line = document.getElementById("interface_nome").textContent;
  const turno = document.getElementById("add_route_turno").value.trim();
  const hr_partida = document
    .getElementById("add_route_horario_partida")
    .value.trim();
  const ht_retorno = document
    .getElementById("add_route_horario_retorno")
    .value.trim();
  const option_selected = return_bool_selected(
    document.getElementById("add_route_options")
  );

  let execute = true;
  if (option_selected) {
    const surname_selected = return_option_selected(
      document.getElementById("add_route_options_container")
    );

    if (surname_selected) {
      var vehicle = surname_selected.split(" ")[0];
    } else {
      execute = false;
      var title = "Nenhuma opção selecionada";
      var text = "Selecione uma opção de veículo disponível.";
    }
  } else {
    var vehicle = "Nenhum";
  }

  if (execute) {
    const data = {
      turno: turno,
      horario_partida: hr_partida,
      horario_retorno: ht_retorno,
      surname: vehicle,
      name_line: name_line,
    };

    popup_button_load("add_route");
    fetch("/create_route", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
      .then((response) => response.json())
      .then((response) => {
        if (!response.error) {
          close_popup("add_route");
          create_popup(response.title, response.text, "Ok", "success");
          loadInterfaceRoutes(name_line);
        } else {
          create_popup(response.title, response.text, "Voltar");
          popup_button_load("add_route", "Criar");
        }
      });
  } else {
    create_popup(title, text, "Voltar");
  }
}

function create_stop(event) {
  event.preventDefault();
  let execute = true;

  const horario_ponto = document
    .getElementById("add_point_route_horario")
    .value.trim();
  const horario_ponto_reverso = document
    .getElementById("add_point_route_horario_inverso")
    .value.trim();
  const container_points = document.getElementById("add_point_route_container");
  const container_options = document.getElementById("add_point_route_options");

  let point_selected = return_option_selected(container_points);
  let option_selected = return_bool_selected(container_options);
  if (!point_selected) {
    execute = false;
    var title = "Nenhum ponto selecionado";
    var text = "Por favor, selecione uma opção disponível para proseguir.";
  } else if (option_selected) {
    if (!horario_ponto_reverso) {
      execute = false;
      var title = "Horário não definido";
      var text = "Nenhum horário para o ponto no trajeto inverso foi definido.";
    }
  }

  if (execute) {
    const data = return_data_route();
    data["name_point"] = point_selected;
    data["type"] = document.getElementById("add_point_route_type").textContent;
    data["time_pas"] = horario_ponto;
    if (option_selected) {
      data["time_pas_2"] = horario_ponto_reverso;
    }

    popup_button_load("add_point_route");
    fetch("/create_stop", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
      .then((response) => response.json())
      .then((response) => {
        if (!response.error) {
          config_popup_route(
            null,
            return_data_route(null, (format_dict_url = true))
          );
          close_popup("add_point_route");
          create_popup(response.title, response.text, "Ok", "success");
        } else {
          create_popup(response.title, response.text, "Voltar");
        }
        document.getElementById("config_route_pos").textContent = data.pos;
      });
  } else {
    create_popup(title, text, "Voltar");
    popup_button_load("add_point_route", "Adicionar");
  }
}

function edit_line(form_submit, event) {
  event.preventDefault();

  let field = form_submit.id.split("_");
  field = field[field.length - 1];

  if (field === "cartela" || field === "diaria") {
    field = "valor_" + field;
  }

  let execute = true;
  const name_line = document.getElementById("interface_nome").textContent;
  const new_value = document.getElementById(`edit_${field}_line_new`);

  const data = {
    name_line: name_line,
    field: field,
    new_value: new_value.value.trim(),
  };
  if (field === "nome" || field === "cidade") {
    const password = document
      .getElementById(`edit_${field}_line_conf`)
      .value.trim();
    data["password"] = password;
  } else if (field === "valor_cartela" || field === "valor_diaria") {
    if (new_value.value === "") {
      var title = "Campo Vazio";
      var text = "O campo não pode estar vazio.";
      execute = false;
    } else if (new_value.value <= 0) {
      var title = "Valor Inválido";
      var text = "O valor deve ser maior que 0.";
      execute = false;
    }
  }

  if (execute) {
    popup_button_load(`edit_${field}_line`);
    fetch("/edit_line", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
      .then((response) => response.json())
      .then((response) => {
        if (!response.error) {
          close_popup(`edit_${field}_line`);

          if (field === "nome") {
            const redirect = `line/${encodeURIComponent(
              new_value.value.trim()
            )}?local_page=linhas`;
            const text =
              "Precisaremos recarregar sua página para ajustar a rota de acesso à sua linha.";
            create_popup(response.title, text, "Ok", "success", redirect);
          } else {
            loadInterfaceLine(name_line, false);
            create_popup(response.title, response.text, "Ok", "success");

            const local = document.getElementById(`config_line_${field}`);
            if (local) {
              local.textContent = new_value.value.trim();
            }
          }
        } else {
          create_popup(response.title, response.text, "Voltar");
          popup_button_load(`edit_${field}_line`, "Alterar");
        }
      });
  } else {
    create_popup(title, text, "Voltar");
  }
}

function edit_calendar() {
  const title = document
    .getElementById("edit_calendar_title")
    .textContent.split(" - ");
  const data = {
    date: title[title.length - 1],
    name_line: document.getElementById("interface_nome").textContent,
    funcionando: return_bool_selected(
      document.getElementById("edit_calendar_options_funcionando")
    ),
    feriado: return_bool_selected(
      document.getElementById("edit_calendar_options_feriado")
    ),
  };

  popup_button_load("edit_calendar");
  fetch("/edit_calendar", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        create_popup(response.title, response.text, "Ok", "success");
        loadInterfaceLine(data.name_line, false);
        close_popup("edit_calendar");
      } else {
        create_popup(response.title, response.text, "Voltar");
        popup_button_load("edit_calendar", "Salvar");
      }
    });
}

function edit_config_line_bool(obj_click) {
  if (!obj_click.querySelector("i").className.includes("selected")) {
    const name_line = document.getElementById("interface_nome").textContent;
    const opcao = obj_click.querySelector("p").textContent;
    const content = document.getElementById("interface_line_content");
    content.classList.add("inactive");

    let field = "paga";
    let new_value = false;

    if (obj_click.parentNode.id.includes("ferias")) {
      field = "ferias";
    }
    if (opcao === "Sim") {
      new_value = true;
      config_bool(obj_click.parentNode, "Sim");
    } else {
      config_bool(obj_click.parentNode, "Não");
    }

    popup_button_load("config_line");
    fetch("/edit_line", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        field: field,
        new_value: new_value,
        name_line: name_line,
      }),
    })
      .then((response) => response.json())
      .then((response) => {
        if (!response.error) {
          loadInterfaceLine(name_line, false);
          content.classList.remove("inactive");
          popup_button_load("config_line", "Fechar");
        } else {
          create_popup(response.title, response.text, "Voltar");
          popup_button_load("config_line", "Fechar");
        }
      });
  }
}

function edit_capacidade_veiculo(event) {
  event.preventDefault();

  const name_line = document.getElementById("interface_nome").textContent;
  const vehicle_surname = document
    .getElementById("edit_vehicle_capacidade")
    .querySelector("span").textContent;
  const new_value = document
    .getElementById("edit_vehicle_capacidade_new")
    .value.trim();

  popup_button_load("edit_vehicle_capacidade");
  fetch("/edit_vehicle", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      field: "capacidade",
      new_value: new_value,
      name_line: name_line,
      surname: vehicle_surname,
    }),
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        close_popup("edit_vehicle_capacidade");
        create_popup(response.title, response.text, "Ok", "success");
        loadInterfaceVehicle(name_line);
      } else {
        create_popup(response.title, response.text, "Voltar");
        popup_button_load("edit_vehicle_capacidade", "Salvar");
      }
    });
}

function edit_motorista_veiculo() {
  const name_line = document.getElementById("interface_nome").textContent;
  const vehicle_surname = document
    .getElementById("edit_vehicle_motorista")
    .querySelector("span").textContent;
  const options_selected = return_option_selected(
    document.getElementById("edit_vehicle_motorista_container")
  );

  if (!options_selected) {
    create_popup(
      "Nenhuma opção selecionada",
      "Por favor, selecione uma opção disponível.",
      "Voltar"
    );
  } else {
    popup_button_load("edit_vehicle_motorista");
    fetch("/edit_vehicle", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        field: "motorista",
        new_value: options_selected,
        name_line: name_line,
        surname: vehicle_surname,
      }),
    })
      .then((response) => response.json())
      .then((response) => {
        if (!response.error) {
          close_popup("edit_vehicle_motorista");
          create_popup(response.title, response.text, "Ok", "success");
          loadInterfaceVehicle(name_line);
          loadInterfaceRoutes(name_line);
        } else {
          create_popup(response.title, response.text, "Voltar");
          popup_button_load("edit_vehicle_motorista", "Salvar");
        }
      });
  }
}

function edit_surname_vehicle(event) {
  event.preventDefault();

  const name_line = document.getElementById("interface_nome").textContent;
  const vehicle_surname = document
    .getElementById("edit_vehicle_surname")
    .querySelector("span").textContent;
  const new_value = document
    .getElementById("edit_vehicle_surname_new")
    .value.trim();

  popup_button_load("edit_vehicle_surname");
  fetch("/edit_vehicle", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      field: "apelido",
      new_value: new_value,
      name_line: name_line,
      surname: vehicle_surname,
    }),
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        close_popup("edit_vehicle_surname");
        create_popup(response.title, response.text, "Ok", "success");
        loadInterfaceVehicle(name_line);
      } else {
        create_popup(response.title, response.text, "Voltar");
        popup_button_load("edit_vehicle_surname", "Salvar");
      }
    });
}

function save_data_description() {
  const name_line = document.getElementById("interface_nome").textContent;
  const surname = document.getElementById(
    "aparence_vehicle_surname"
  ).textContent;
  const local = document.getElementById("aparence_vehicle_description");
  const text = local.querySelector("textarea");

  if (text) {
    popup_button_load("aparence_vehicle", "Salvando...");
    fetch("/edit_aparence", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        field: "description",
        new_value: text.value.trim(),
        name_line: name_line,
        surname: surname,
      }),
    })
      .then((response) => response.json())
      .then((response) => {
        if (response.error) {
          create_popup(response.title, response.text);
        }
      });
  }
  close_popup("aparence_vehicle");
}

function edit_aparence(obj_click, event) {
  event.preventDefault();

  const name_line = document.getElementById("interface_nome").textContent;
  const surname = document.getElementById(
    "aparence_vehicle_surname"
  ).textContent;

  let field = obj_click.id.split("_");
  field = field[field.length - 1];
  const new_value = obj_click.querySelector('[id*="new"]').value.trim();

  popup_button_load("edit_aparence_" + field);
  fetch("/edit_aparence", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      field: field,
      new_value: new_value,
      name_line: name_line,
      surname: surname,
    }),
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        close_popup("edit_aparence_" + field);
        config_popup_aparence(surname);
        create_popup(response.title, response.text, "Ok", "success");
      } else {
        create_popup(response.title, response.text, "Voltar");
        popup_button_load("edit_aparence_" + field, "Salvando");
      }
    });
}

function edit_point(form_submit, event) {
  event.preventDefault();

  let field = form_submit.id.split("_");
  field = field[field.length - 1];
  if (field === "tolerancia") {
    field = "tempo_tolerancia";
  }

  const new_value = form_submit.querySelector("input").value.trim();
  const name_line = document.getElementById("interface_nome").textContent;
  const name_point = document.getElementById("config_point_nome").textContent;

  popup_button_load("edit_point_" + field);
  fetch("/edit_point", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      field: field,
      new_value: new_value,
      name_line: name_line,
      name_point: name_point,
    }),
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        close_popup("edit_point_" + field);
        create_popup(response.title, response.text, "Ok", "success");
        loadInterfacePoints(name_line);
        document.getElementById("config_point_" + field).textContent =
          new_value;
      } else {
        create_popup(response.title, response.text, "Voltar");
        popup_button_load("edit_point_" + field, "Salvar");
      }
    });
}

function edit_route(obj_reference, event = false) {
  if (event) {
    event.preventDefault();
  }

  let field = obj_reference.id.split("_");
  field = field[field.length - 1];

  if (field === "partida" || field === "retorno") {
    field = "horario_" + field;
  }

  let execute = true;
  if (field === "onibus") {
    const container = document.getElementById("edit_route_onibus_container");
    const item_selected = container.querySelector('[class*="selected"]');
    if (item_selected) {
      var new_value = item_selected
        .querySelector("p")
        .textContent.trim()
        .split(" ")[0];
    } else {
      create_popup(
        "Nenhuma opção selecionada",
        "Por favor, selecione uma opção disponível.",
        "Voltar"
      );
      execute = false;
    }
  } else {
    var new_value = obj_reference.querySelector("input").value.trim();
  }

  if (execute) {
    const data = return_data_route();
    data["field"] = field;
    data["new_value"] = new_value;

    popup_button_load(obj_reference.id.replace("formulario_", ""));
    fetch("/edit_route", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
      .then((response) => response.json())
      .then((response) => {
        if (!response.error) {
          const btn_route = document.getElementById("interface_rotas_btn");
          if (field === "onibus") {
            action_container(btn_route);
          }
          loadInterfaceRoutes(data.name_line);
          const local_popup = document.getElementById("popup_local");
          local_popup.removeChild(local_popup.querySelector("#config_route"));

          close_popup(obj_reference.id.replace("formulario_", ""));
          create_popup(response.title, response.text, "Ok", "success");
        } else {
          create_popup(response.title, response.text, "Voltar");
          popup_button_load(
            obj_reference.id.replace("formulario_", ""),
            "Alterar"
          );
        }
      });
  }
}

function edit_horario_relationship() {
  const new_horario = document
    .getElementById("edit_horario_relacao_ponto_rota_new_horario")
    .value.trim();
  const data = return_data_route();
  data["type"] = document
    .getElementById("config_rel_point_route_tipo")
    .textContent.toLowerCase();
  data["name_point"] = document.getElementById(
    "config_rel_point_route_nome"
  ).textContent;
  data["field"] = "horario_passagem";
  data["new_value"] = new_horario;

  popup_button_load("edit_horario_relacao_ponto_rota");
  fetch("/edit_relationship-ponto", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        const local_popup = document.getElementById("popup_local");
        local_popup.removeChild(
          local_popup.querySelector("#config_rel_point_route")
        );

        close_popup("edit_horario_relacao_ponto_rota");
        config_popup_route(
          null,
          return_data_route(null, (format_dict_url = true))
        );
        create_popup(response.title, response.text, "Ok", "success");
      } else {
        create_popup(response.title, response.text, "Voltar");
        popup_button_load("edit_horario_relacao_ponto_rota", "Alterar");
      }
    });
}

function save_data_route() {
  const container_partida = Array.from(
    document.getElementById("config_route_pontos_partida_area").children
  );
  const container_retorno = Array.from(
    document.getElementById("config_route_pontos_retorno_area").children
  );
  const data = return_data_route();
  data["partida"] = [];
  data["retorno"] = [];

  container_partida.forEach((parada) => {
    data.partida.push(extract_info(parada, "nome"));
  });
  container_retorno.forEach((parada) => {
    data.retorno.push(extract_info(parada, "nome"));
  });

  popup_button_load("config_route", "Salvando...");
  fetch("/edit_order_stop", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((response) => {
      if (response.error) {
        create_popup(response.title, response.text, "Ok");
      }
    });
  close_popup("config_route");
}

function del_vehicle() {
  const name_line = document.getElementById("interface_nome").textContent;
  const surname = document.getElementById("del_vehicle_surname").textContent;
  const data = {
    principal: [name_line, surname],
  };

  popup_button_load("del_vehicle");
  fetch("/del_vehicle" + generate_url_dict(data), { method: "DELETE" })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        close_popup("del_vehicle");
        create_popup(response.title, response.text, "Ok", "success");
        loadInterfaceVehicle(name_line);
        loadInterfaceRoutes(name_line);
      } else {
        create_popup(response.title, response.text, "Voltar");
        popup_button_load("del_vehicle", "Excluir");
      }
    });
}

function del_relationship_point_route() {
  const data = return_data_route(null, (format_dict_url = true));
  data.principal.push(
    document.getElementById("config_rel_point_route_tipo").textContent,
    document.getElementById("config_rel_point_route_nome").textContent
  );

  popup_button_load("del_relationship_point_route");
  fetch("/del_relationship_point_route" + generate_url_dict(data), {
    method: "DELETE",
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        local_popup.removeChild(
          local_popup.querySelector("#config_rel_point_route")
        );
        close_popup("del_relationship_point_route");
        create_popup(response.title, response.text, "Ok", "success");
        config_popup_route(
          null,
          return_data_route(null, (format_dict_url = true))
        );
        loadInterfaceRoutes(name_line);
      } else {
        create_popup(response.title, response.text, "Voltar");
        popup_button_load("del_relationship_point_route", "Excluir");
      }
    });
}

function del_route(event) {
  event.preventDefault();
  const data = return_data_route();
  data.password = document.getElementById("del_route_conf").value.trim();

  popup_button_load("del_route");
  fetch("/del_route", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        const btn_route = document.getElementById("interface_rotas_btn");
        action_container(btn_route);

        local_popup.removeChild(local_popup.querySelector("#config_route"));
        close_popup("del_route");
        create_popup(response.title, response.text, "Ok", "success");

        loadInterfaceRoutes(data.name_line);
        loadInterfaceStudents(data.name_line);
      } else {
        create_popup(response.title, response.text, "Voltar");
        popup_button_load("del_route", "Excluir");
      }
    });
}

function del_point(event) {
  event.preventDefault();
  const name_line = document.getElementById("interface_nome").textContent;
  const name_point = document.getElementById("del_ponto_nome").textContent;
  const data = { principal: [name_line, name_point] };

  popup_button_load("del_ponto");
  fetch("/del_point" + generate_url_dict(data), { method: "DELETE" })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        const btn_point = document.getElementById("interface_pontos_btn");
        action_container(btn_point);

        local_popup.removeChild(local_popup.querySelector("#config_point"));
        close_popup("del_ponto");
        create_popup(response.title, response.text, "Ok", "success");

        loadInterfacePoints(name_line);
        loadInterfaceStudents(name_line);
      } else {
        create_popup(response.title, response.text, "Voltar");
        popup_button_load("del_ponto", "Excluir");
      }
    });
}

function del_line(event) {
  event.preventDefault();
  const name_line = document.getElementById("interface_nome").textContent;
  const password = document.getElementById("del_linha_conf").value.trim();
  const data = { name_line: name_line, password: password };

  popup_button_load("del_linha");
  fetch("/del_line", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        local_popup.removeChild(local_popup.querySelector("#config_line"));
        close_popup("del_linha");
        create_popup(
          response.title,
          response.text,
          "Ok",
          "success",
          "page_user?local=linhas"
        );
      } else {
        create_popup(response.title, response.text, "Voltar");
        popup_button_load("del_linha", "Excluir");
      }
    });
}

function migrate_by_defect() {
  let execute = true;
  const container_vehicles = document.getElementById(
    "transfer_by_defect_veiculo_container"
  );
  const container_shifts = document.getElementById(
    "transfer_by_defect_shifts_container"
  );

  const selected_vehicle = return_option_selected(container_vehicles, true);
  const selected_shifts = return_option_selected(container_shifts, true);

  if (!selected_shifts) {
    execute = false;
    var title = "Nenhum Turno Selecionado";
    var text =
      "Você precisa selecionar pelo menos um turno que será afetado pelo defeito do veículo.";
  } else if (!selected_vehicle) {
    execute = false;
    var title = "Nenhum Veículo Selecionado";
    var text =
      "Você precisa selecionar pelo menos um veículo para transferir os participantes do transporte atual.";
  }

  if (execute) {
    const data = {
      name_line: document.getElementById("interface_nome").textContent.trim(),
      surname: document
        .getElementById("transfer_by_defect_info_vehicle")
        .textContent.trim(),
      targets: selected_vehicle.map((item) => item.split(" ")[0]),
      shifts: selected_shifts,
    };

    popup_button_load("transfer_by_defect");
    fetch("/migrate_defect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
      .then((response) => response.json())
      .then((response) => {
        if (!response.error) {
          loadInterfaceVehicle(data.name_line);
          local_popup.removeChild(
            local_popup.querySelector("#transfer_by_defect_info")
          );
          close_popup("transfer_by_defect");
          create_popup(response.title, response.text, "Ok", "success");
        } else {
          popup_button_load("transfer_by_defect", "Marcar");
          create_popup(response.title, response.text);
        }
      });
  } else {
    create_popup(title, text);
  }
}

function remove_migrate_by_defect() {
  const name_line = document
    .getElementById("interface_nome")
    .textContent.trim();
  const surname = document
    .getElementById("remove_transfer_by_defect_vehicle")
    .textContent.trim();
  const data = {
    principal: [name_line, surname],
  };

  popup_button_load("remove_transfer_by_defect");
  fetch("/del_migrate_defect" + generate_url_dict(data), { method: "DELETE" })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        create_popup(response.title, response.text, "Ok", "success");
        close_popup("remove_transfer_by_defect");
        loadInterfaceVehicle(name_line);
      } else {
        popup_button_load("remove_transfer_by_defect", "Desmarcar");
        create_popup(response.title, response.text);
      }
    });
}
