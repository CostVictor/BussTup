templates = document.getElementById("templates_model");
models = document.importNode(templates.content, true);

function loadInterfaceLine(name_line, load_complete = true) {
  fetch(`/get_interface-line/${encodeURIComponent(name_line)}`, {
    method: "GET",
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        let adm = false;
        const aviso_entrada = document.getElementById("interface_line_enter");
        aviso_entrada.classList.add("inactive");

        if (response.role === "motorista") {
          const config_linha = document.getElementById("interface_config");
          config_linha.classList.add("inactive");

          if (response.relacao) {
            if (response.relacao === "dono") {
              config_linha.classList.remove("inactive");
              adm = true;
            } else if (response.relacao === "adm") {
              adm = true;
            }
          } else {
            aviso_entrada.classList.remove("inactive");
          }
        } else {
          if (!response.relacao || response.relacao === "não participante") {
            aviso_entrada.classList.remove("inactive");
          }
        }

        for (dado in response.data) {
          if (dado === "paga") {
            const area_paga = document.getElementById("area_paga");
            if (!response.data[dado]) {
              area_paga.classList.add("inactive");
            } else {
              area_paga.classList.remove("inactive");
            }
          } else if (dado === "ferias") {
            const info_ferias = document.getElementById("interface_ferias");
            if (!response.data[dado]) {
              info_ferias.classList.add("inactive");
            } else {
              info_ferias.classList.remove("inactive");
            }
          } else {
            const info = document.getElementById(`interface_${dado}`);
            const edit = document.getElementById(
              info.id.replace("interface", "edit")
            );
            info.textContent = response.data[dado];

            if (edit) {
              if (adm) {
                edit.classList.remove("inactive");
              } else {
                edit.classList.add("inactive");
              }
            }
          }
        }

        if (load_complete) {
          loadInterfaceDriver(name_line);
          loadInterfaceVehicle(name_line);
          if (response.role === "motorista") {
            loadInterfacePoints(name_line);
            loadInterfaceStudents(name_line);
          }
          loadInterfaceRoutes(name_line);
        }
      } else {
        create_popup(response.title, response.text, "Voltar");
      }
      const elements = document.querySelectorAll('[class*="-enter-"]');
      animate_itens(elements, "fadeDown", 0.6, 0.2);
    });
}

function loadInterfaceDriver(name_line) {
  fetch(`/get_interface-driver/${encodeURIComponent(name_line)}`, {
    method: "GET",
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        const data = response.data;
        const local_motorista = document.getElementById("area_motoristas");
        const elements_remove = Array.from(local_motorista.children);
        elements_remove.forEach((element) => {
          if (element.id.includes("motorista")) {
            local_motorista.removeChild(element);
          }
        });
        local_motorista.removeChild(local_motorista.querySelector("span"));

        const model_motorista = models.querySelector("#model_motorista");
        for (tipo in data) {
          for (pos in data[tipo]) {
            const motorista = model_motorista.cloneNode(true);
            motorista.id = `motorista_${tipo}-${pos}`;

            const ids = motorista.querySelectorAll('[id*="model_motorista"]');
            ids.forEach((element) => {
              element.id = element.id.replace("model_motorista", motorista.id);
            });
            for (info in data[tipo][pos]) {
              const tag = motorista.querySelector(`[id*="${info}"]`);
              tag.textContent = data[tipo][pos][info];
            }

            const dono = motorista.querySelector('[id*="dono"]');
            const adm = motorista.querySelector('[id*="adm"]');
            if (response.role === "motorista") {
              if (response.relacao === "dono" && tipo !== "dono") {
                const btn_config = motorista.querySelector('[id*="btn"]');
                btn_config.classList.remove("inactive");
              }
            }
            if (tipo === "dono") {
              dono.classList.remove("inactive");
              adm.classList.remove("inactive");
            } else if (tipo === "adm") {
              adm.classList.remove("inactive");
            }

            motorista.classList.remove("inactive");
            local_motorista.appendChild(motorista);
          }
        }
      } else {
        create_popup(response.title, response.text, "Voltar");
      }
    });
}

function adicionar_veiculo(model, list, container, response) {
  container.innerHTML = "";

  for (index in list) {
    const vehicle = model.cloneNode(true);
    vehicle.id = `${container.id}-veiculo_${index}`;

    ids = vehicle.querySelectorAll(`[id*="${model.id}"]`);
    ids.forEach((item) => {
      item.id = item.id.replace(model.id, vehicle.id);
    });

    const dados = list[index];
    for (dado in dados) {
      const value = dados[dado];
      const info = vehicle.querySelector(`[id*="${dado}"]`);
      info.textContent = value;

      if (response.role == "motorista") {
        let icon = info.parentNode.querySelector("i");
        if (dado === "capacidade") {
          icon = info.parentNode.parentNode.querySelector("i");
        }

        if (icon && icon.className.includes("pencil")) {
          if (response.relacao) {
            if (
              response.relacao !== "membro" ||
              value === "Nenhum" ||
              value === response.meu_nome
            ) {
              icon.classList.remove("inactive");
            }
          }
        }
      }
    }

    if (
      response.role == "motorista" &&
      response.relacao &&
      response.relacao !== "membro"
    ) {
      vehicle
        .querySelector('[id*="division_edit"]')
        .classList.remove("inactive");

      vehicle
        .querySelector('[id*="edit_apelido"]')
        .classList.remove("inactive");

      vehicle.querySelector('[id*="delete"]').classList.remove("inactive");
    }
    container.appendChild(vehicle);
  }
}

function loadInterfaceVehicle(name_line) {
  fetch(`/get_interface-vehicle/${encodeURIComponent(name_line)}`, {
    method: "GET",
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        const model_vehicle = models.querySelector("#model_vehicle");
        const container_sem = document.getElementById(
          "area_vehicle_content_sem_condutor"
        );
        const container_com = document.getElementById(
          "area_vehicle_content_com_condutor"
        );
        const division_local = document.getElementById(
          "area_vehicle_division_vehicle"
        );
        const local_vehicle = document.getElementById("area_vehicle");

        const com_mot = response.data.com_condutor;
        const sem_mot = response.data.sem_condutor;

        adicionar_veiculo(model_vehicle, com_mot, container_com, response);
        adicionar_veiculo(model_vehicle, sem_mot, container_sem, response);

        if (sem_mot.length && com_mot.length) {
          division_local.classList.remove("inactive");
        } else {
          division_local.classList.add("inactive");
        }

        if (response.role == "motorista") {
          const division = document.getElementById("area_vehicle_division_add");
          const btn_add = document.getElementById("area_vehicle_btn_add");

          if (response.relacao && response.relacao !== "membro") {
            btn_add.classList.remove("inactive");
            if (com_mot.length || sem_mot.length) {
              local_vehicle.removeChild(local_vehicle.querySelector("span"));
              division.classList.remove("inactive");
            } else {
              const text = local_vehicle.querySelector("span");
              text.textContent = "Nenhum veículo cadastrado";
              text.className =
                "text secundario fundo cinza justify margin_bottom";
            }
          }
        } else {
          if (com_mot.length || sem_mot.length) {
            local_vehicle.removeChild(local_vehicle.querySelector("span"));
          } else {
            const text = local_vehicle.querySelector("span");
            text.textContent = "Nenhum veículo cadastrado";
            text.className = "text secundario fundo cinza justify";
          }
        }
      } else {
        create_popup(response.title, response.text);
      }
    });
}

function config_popup_aparence(surname_vehicle) {
  const name_line = document.getElementById("interface_nome").textContent;
  data = { principal: [name_line, surname_vehicle] };

  fetch("/get_aparence" + generate_url_dict(data), {
    method: "GET",
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        const data = response.data;
        for (dado in data) {
          const value = data[dado];
          const info = document.getElementById(`aparence_vehicle_${dado}`);

          if (response.role === "motorista") {
            const model_textarea = models.querySelector("#model_description");
            const icon = info.parentNode.querySelector("i");

            if (response.relacao && response.relacao !== "membro") {
              if (icon) {
                icon.classList.remove("inactive");
              }

              if (dado === "description") {
                const text = model_textarea.cloneNode(true);
                text.value = value;
                info.innerHTML = "";
                info.appendChild(text);
              } else {
                info.textContent = value;
              }
            } else {
              if (icon) {
                icon.classList.add("inactive");
              }

              if (dado === "description") {
                const text = document.createElement("p");
                text.className = "text secundario content fundo justify";
                text.textContent = value;
                info.innerHTML = "";
                info.appendChild(text);
              } else {
                info.textContent = value;
              }
            }
          } else {
            info.textContent = value;
          }
        }
      } else {
        create_popup(response.title, response.text);
      }
    });
}

function criar_rota(
  list,
  container,
  format_min = false,
  selected = false,
  compare = false
) {
  const model_rota = models.querySelector("#model_interface_rota");
  container.innerHTML = "";

  for (index in list) {
    const route = model_rota.cloneNode(true);
    if (format_min) {
      route.querySelector("div.popup__input_big").classList.add("max");
      route.querySelector("p.display").classList.add("min");
    }
    route.id = `${container.id}-rota_${index}`;

    ids = route.querySelectorAll(`[id*="${model_rota.id}"]`);
    ids.forEach((value) => {
      value.id = value.id.replace(model_rota.id, route.id);
    });

    const dados = list[index];
    for (dado in dados) {
      route.querySelector(`[id*="${dado}"]`).textContent = dados[dado];
    }

    delete dados.quantidade;
    if (compare) {
      if (Array.isArray(compare)) {
        for (pos in compare) {
          const item = compare[pos][0];
          if (item) {
            delete item.quantidade;
            if (JSON.stringify(item) === JSON.stringify(dados)) {
              route.classList.add("selected");
            }
          } else {
            delete compare[pos].quantidade;
            if (JSON.stringify(compare[pos]) === JSON.stringify(dados)) {
              route.classList.add("selected");
            }
          }
        }
      } else {
        delete compare.quantidade;
        if (JSON.stringify(compare) === JSON.stringify(dados)) {
          route.classList.add("selected");
        }
      }
    }

    if (index) {
      const dados_ant = list[index - 1];
      if (JSON.stringify(dados) === JSON.stringify(dados_ant)) {
        const route_ant = document.getElementById(
          `${container.id}-rota_${index - 1}`
        );
        const span_ant = route_ant.querySelector("span");
        if (!span_ant.textContent) {
          span_ant.textContent = 0;
        }
        route.querySelector("span").textContent =
          parseInt(span_ant.textContent) + 1;
      }
    }
    if (selected) {
      route.classList.add("selected");
    }

    route.classList.remove("inactive");
    container.appendChild(route);
  }
}

function config_popup_routes_vehicle(surname_vehicle) {
  const name_line = document.getElementById("interface_nome").textContent;
  data = { principal: [name_line, surname_vehicle] };

  fetch("/get_interface-option_route_vehicle" + generate_url_dict(data), {
    method: "GET",
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        const data = response.data;
        const container = document.getElementById(
          "vehicle_utilities_routes_container"
        );
        if (data.length) {
          criar_rota(data, container, true);
        } else {
          const text = document.createElement("p");
          text.className = "text info center fundo cinza";
          text.textContent = "Nenhuma rota encontrada";
          container.appendChild(text);
        }
      } else {
        create_popup(response.title, response.text);
      }
    });
}

function loadInterfaceRoutes(name_line) {
  fetch(`/get_interface-routes/${encodeURIComponent(name_line)}`, {
    method: "GET",
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        const local_ativas = document.getElementById("interface_rotas_ativas");
        const ativas = response.ativas;

        if (response.role == "motorista") {
          const local_desativas = document.getElementById(
            "interface_rotas_desativas"
          );
          const division_desativas = document.getElementById(
            "interface_rotas_desativas_division"
          );
          const title_desativas = document.getElementById(
            "interface_rotas_desativas_title"
          );
          const desativas = response.desativas;

          local_desativas.classList.add("inactive");
          division_desativas.classList.add("inactive");
          title_desativas.classList.add("inactive");

          document.getElementById("interface_rotas_quantidade").textContent =
            response.quantidade;
          const route_division = document.getElementById(
            "interface_rotas_division"
          );
          const route_add = document.getElementById("interface_rotas_add");

          route_division.classList.add("inactive");
          route_add.classList.add("inactive");

          if (response.relacao && response.relacao !== "membro") {
            route_add.classList.remove("inactive");
            if (ativas.length || desativas.length) {
              route_division.classList.remove("inactive");
            }
          }
          if (desativas.length) {
            local_desativas.classList.remove("inactive");
            title_desativas.classList.remove("inactive");
            if (ativas.length) {
              division_desativas.classList.remove("inactive");
            }
          }
          criar_rota(desativas, local_desativas);
          criar_rota(ativas, local_ativas);
        } else {
          const area_rotas = document.getElementById("area_rotas");
          const local_minhas_rotas = document.getElementById(
            "interface_rotas_minhas_rotas"
          );

          if (response.relacao === "participante") {
            local_minhas_rotas.classList.remove("inactive");
            const local_msgs = local_minhas_rotas.querySelector("span");
            const division = document.getElementById(
              "interface_rotas_division"
            );
            const minhas_rotas = response.minhas_rotas;

            const span_txt = document.getElementById("area_rotas_span_text");
            if (span_txt) {
              if (Object.values(minhas_rotas).length || ativas.length) {
                area_rotas.removeChild(span_txt);
              } else {
                span_txt.textContent = "Nenhuma rota cadastrada";
                span_txt.className = "text secundario fundo cinza justify";
              }
            }

            local_msgs.innerHTML = "";
            const mensagens = response.mensagens;
            if (mensagens.length) {
              for (index in mensagens) {
                const text = document.createElement("p");
                text.className = "text info fundo cinza";
                text.textContent = mensagens[index];
                local_msgs.appendChild(text);
              }
              const text = document.createElement("h1");
              text.className = "page__division";
              local_msgs.appendChild(text);
            }

            for (tipo in minhas_rotas) {
              const area_local = document.getElementById(
                "interface_rotas_minhas_rotas_" + tipo
              );
              if (minhas_rotas[tipo].length) {
                area_local.classList.remove("inactive");
                const container = area_local.querySelector("div");
                criar_rota(minhas_rotas[tipo], container);
              } else {
                area_local.classList.add("inactive");
              }
            }

            division.classList.add("inactive");
            if (ativas.length) {
              division.classList.remove("inactive");
            }

            criar_rota(ativas, local_ativas, false, false, [
              minhas_rotas.turno,
              minhas_rotas.contraturno,
            ]);
          } else {
            local_minhas_rotas.classList.add("inactive");
            criar_rota(ativas, local_ativas);

            if (ativas.length) {
              area_rotas.removeChild(area_rotas.querySelector("span"));
            } else {
              const span_txt = area_rotas.querySelector("span");
              span_txt.textContent = "Nenhuma rota cadastrada";
              span_txt.className = "text secundario fundo cinza justify";
            }
          }
        }
      } else {
        create_popup(response.title, response.text, "Voltar");
      }
    });
}

function config_popup_route(obj_click, data = false) {
  if (!data) {
    data = return_data_route(obj_click, (format_dict_url = true));
  }
  document.getElementById("config_route_pos").textContent = data.pos;
  close_popup("vehicle_utilities_routes");
  close_popup("config_point");

  fetch("/get_route" + generate_url_dict(data), { method: "GET" })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        const msg_desativada = document.getElementById(
          "config_route_desativada"
        );
        const data = response.data;
        const information = response.info;
        const role = response.role;
        const relacao = response.relacao;

        msg_desativada.classList.add("inactive");
        if (response.msg_desativada) {
          msg_desativada.classList.remove("inactive");
        }

        if (role === "aluno") {
          const msg_cadastrar = document.getElementById(
            "config_route_aviso_cadastrar"
          );

          const msg_incompleta = document.getElementById(
            "config_route_aviso_incompleto"
          );

          const msg_incompleta_txt = document.getElementById(
            "config_route_aviso_incompleto_txt"
          );

          const msg_contraturno = document.getElementById(
            "config_route_aviso_contraturno"
          );
          const btn_contraturno = document.getElementById(
            "config_route_btn_contraturno"
          );
          const container_contraturno = document.getElementById(
            "config_route_contraturno_container"
          );

          msg_cadastrar.classList.add("inactive");
          msg_incompleta.classList.add("inactive");
          msg_contraturno.classList.add("inactive");
          btn_contraturno.classList.add("inactive");
          container_contraturno.classList.add("inactive");
          if (response.msg_cadastrar) {
            msg_cadastrar.classList.remove("inactive");
          } else {
            if (response.msg_incompleta) {
              msg_incompleta_txt.textContent = `Você não definiu seu ponto fixo de ${response.incompleta}.`;
              msg_incompleta.classList.remove("inactive");
            }

            if (response.msg_contraturno) {
              msg_contraturno.classList.remove("inactive");
            }

            if (response.btn_contraturno) {
              btn_contraturno.classList.remove("inactive");
            }

            if (response.meu_contraturno) {
              container_contraturno.classList.remove("inactive");
              container_contraturno.querySelector(
                "#config_route_contraturno"
              ).textContent = response.meu_contraturno;
            }
          }
        } else {
          const route_division = document.getElementById("route_division");
          const route_del = document.getElementById("route_del");

          if (relacao && relacao !== "membro") {
            route_division.classList.remove("inactive");
            route_del.classList.remove("inactive");
          } else {
            route_division.classList.add("inactive");
            route_del.classList.add("inactive");
          }
        }

        const popup = document.getElementById("config_route");
        for (nome in information) {
          const value = information[nome];
          const info = popup.querySelector(`[id*="${nome}"]`);
          info.textContent = value;
          if (role == "motorista") {
            const icon = info.parentNode.querySelector("i");
            if (icon) {
              if (relacao && relacao !== "membro") {
                icon.classList.remove("inactive");
              } else {
                icon.classList.add("inactive");
              }
            }
          }
        }

        const model_relacao = models.querySelector(
          "#interface_model_option_headli"
        );
        for (nome in data) {
          const tipo = data[nome];
          const paradas = tipo.paradas;
          const btn_aba = document.getElementById(
            `config_route_pontos_container_${nome}_btn`
          );
          const container = popup.querySelector(`[id*="${nome}_area"]`);
          container.innerHTML = "";

          if (return_btn_open(btn_aba)) {
            action_container(btn_aba);
          }
          if (role === "motorista") {
            const area_division = container.parentNode.querySelector("h1");
            const area_add = container.parentNode.querySelector("div.justify");

            area_division.classList.add("inactive");
            area_add.classList.add("inactive");
            if (relacao && relacao !== "membro") {
              area_add.classList.remove("inactive");
              if (paradas.length) {
                area_division.classList.remove("inactive");
              }
            }
          }

          popup.querySelector(`[id*="quantidade_${nome}"]`).textContent =
            tipo.quantidade;
          for (index in paradas) {
            const relacao = model_relacao.cloneNode(true);
            relacao.id = `${container.id}-relacao_${index}`;

            ids = relacao.querySelectorAll(`[id*="${model_relacao.id}"]`);
            ids.forEach((element) => {
              element.id = element.id.replace(model_relacao.id, relacao.id);
            });

            dados = paradas[index];
            for (dado in dados) {
              const value = dados[dado];
              const item = relacao.querySelector(`[id*="${dado}"]`);
              item.textContent = value;

              if (role == "aluno" && response.meus_pontos) {
                const meu_ponto = response.meus_pontos[nome];
                if (meu_ponto === dados.nome) {
                  item.classList.add("selected");
                }
              }
            }

            if (role === "motorista") {
              icon = relacao.querySelector("i");
              icon.classList.add("inactive");
              if (response.relacao && response.relacao !== "membro") {
                icon.classList.remove("inactive");
              }
            }

            relacao.classList.remove("inactive");
            container.appendChild(relacao);
          }
        }
      } else {
        close_popup("config_route");
        create_popup(response.title, response.text, "Voltar");
      }
    });
}

function config_popup_relationship(data) {
  fetch("/get_relationship-point" + generate_url_dict(data), { method: "GET" })
    .then((response) => response.json())
    .then((response) => {
      const data = response.data;

      for (dado in data) {
        const value = data[dado];
        const info = document.getElementById(`config_rel_point_route_${dado}`);
        info.textContent = value;

        if (response.role == "motorista") {
          const icon = info.parentNode.querySelector("i");
          if (icon) {
            if (response.relacao && response.relacao !== "membro") {
              icon.classList.remove("inactive");
            } else {
              icon.classList.add("inactive");
            }
          }
        }
      }

      if (response.role === "motorista") {
        const model_aluno = models.querySelector("#interface_model_aluno");
        const cadastrados = response.cadastrados;
        for (tipo in cadastrados) {
          document.getElementById(
            `config_rel_point_route_${tipo}_quantidade`
          ).textContent = cadastrados[tipo].quantidade;
          const alunos = cadastrados[tipo].alunos;
          const container = document.getElementById(
            `config_rel_point_route_${tipo}_container`
          );
          criar_aluno(alunos, container, response, model_aluno);
        }

        const division = document.getElementById(
          "config_rel_point_route_division"
        );
        const del = document.getElementById("config_rel_point_route_del");

        division.classList.add("inactive");
        del.classList.add("inactive");
        if (response.relacao && response.relacao !== "membro") {
          division.classList.remove("inactive");
          del.classList.remove("inactive");
        }
      } else {
        if (!response.contraturno) {
          const btn_cadastrar = document.getElementById(
            "config_rel_point_route_cadastrar"
          );
          const btn_sair = document.getElementById(
            "config_rel_point_route_sair"
          );

          btn_cadastrar.classList.add("inactive");
          btn_sair.classList.add("inactive");
          if (response.cadastrado) {
            btn_sair.classList.remove("inactive");
          } else {
            btn_cadastrar.classList.remove("inactive");
          }
        } else {
          document
            .getElementById("config_rel_point_route_division")
            .classList.add("inactive");
        }
      }
    });
}

function return_data_route(obj_model = false, format_dict_url = false) {
  const name_line = document.getElementById("interface_nome").textContent;
  if (obj_model) {
    var surname = extract_info(obj_model, "apelido");
    var shift = extract_info(obj_model, "turno");
    var time_par = extract_info(obj_model, "horario_partida");
    var time_ret = extract_info(obj_model, "horario_retorno");
    var pos = obj_model.querySelector("span").textContent;
  } else {
    var surname = document.getElementById("config_route_onibus").textContent;
    var shift = document.getElementById("config_route_turno_rota").textContent;
    var time_par = document.getElementById(
      "config_route_horario_partida"
    ).textContent;
    var time_ret = document.getElementById(
      "config_route_horario_retorno"
    ).textContent;
    var pos = document.getElementById("config_route_pos").textContent;
  }

  if (format_dict_url) {
    return {
      principal: [name_line, surname, shift, time_par, time_ret],
      secondary: pos ? { pos: pos } : {},
    };
  }
  return {
    name_line: name_line,
    surname: surname,
    shift: shift,
    time_par: time_par,
    time_ret: time_ret,
    pos: pos,
  };
}
