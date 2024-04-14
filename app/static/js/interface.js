function extract_info(obj_click, reference, local = "id") {
  const verify = obj_click.querySelector(`[${local}*="${reference}"]`);
  if (verify) {
    return verify.textContent;
  }

  let tag = obj_click.parentNode;
  while (true) {
    var identify_nome = tag.querySelector(`[${local}*="${reference}"]`);
    if (identify_nome) {
      return identify_nome.textContent;
    } else {
      tag = tag.parentNode;
    }
  }
}

function copy_text(obj_click = null) {
  const icons = document.querySelectorAll('[class*="copy"]');

  icons.forEach((icon) => {
    if (icon === obj_click) {
      icon.classList.replace("bi-clipboard", "bi-check-lg");
      const div_pai = icon.parentNode;
      const element_text = div_pai.querySelector("p.content");
      navigator.clipboard.writeText(element_text.innerText);
    } else {
      icon.classList.replace("bi-check-lg", "bi-clipboard");
    }
  });
}

function generate_url_dict(dict_reference) {
  const keys = Object.keys(dict_reference);
  let url = "";

  if (keys.includes("principal") && dict_reference.principal.length) {
    let principal = [];
    for (index in dict_reference.principal) {
      let value = dict_reference.principal[index];
      principal.push(encodeURIComponent(value));
    }
    url = "/" + principal.join("/");
  }

  if (keys.includes("secondary") && dict_reference.secondary) {
    let results = [];
    const keys_secondary = Object.keys(dict_reference.secondary);
    keys_secondary.forEach((key) => {
      results.push(
        `${key}=${encodeURIComponent(dict_reference.secondary[key])}`
      );
    });
    if (results.length) {
      url += `?${results.join("&")}`;
    }
  }
  return url;
}

function return_option_selected(container_options) {
  let option_selected = container_options.querySelector('[class*="selected"]');
  if (option_selected) {
    return option_selected.textContent.trim();
  }
  return false;
}

function return_bool_selected(container_options) {
  let option_selected =
    container_options.querySelector("i.selected").parentNode;
  option_selected = option_selected.querySelector("p").textContent;
  if (option_selected === "Sim") {
    return true;
  }
  return false;
}

function return_text_bool_selected(container_options) {
  let option_selected =
    container_options.querySelector("i.selected").parentNode;
  return option_selected.querySelector("p").textContent;
}

function return_btn_open(btn) {
  const icon = btn.querySelector("i");
  if (icon.className.includes("open")) {
    return true;
  }
  return false;
}

function include_options_container(
  container,
  option,
  dict,
  option_nenhum = false,
  set_limit = false,
  model_id = "model_option"
) {
  const model = models.querySelector(`#${model_id}`);

  if (option_nenhum) {
    const nenhum = model.cloneNode(true);
    nenhum.id = `${container.id}-option_nenhum`;
    nenhum.querySelector("p").textContent = "Nenhum";

    ids = nenhum.querySelectorAll(`[id*="${model_id}"]`);
    ids.forEach((element) => {
      element.id = element.id.replace(model_id, nenhum.id);
    });

    nenhum.classList.remove("inactive");
    container.appendChild(nenhum);
  }

  fetch(`/get_interface-${option}` + generate_url_dict(dict), { method: "GET" })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        let data = response.data;

        if (data.length) {
          for (index in data) {
            const value = data[index];
            const option = model.cloneNode(true);

            option.id = `${container.id}-option_${index}`;
            option.querySelector("p").textContent = value;

            const ids = option.querySelectorAll(`[id*="${model_id}"]`);
            ids.forEach((element) => {
              element.id = element.id.replace(model_id, option.id);
            });

            option.classList.remove("inactive");
            container.appendChild(option);
          }

          if (set_limit) {
            set_limitScroll(container);
          }
        } else if (!option_nenhum) {
          const text = document.createElement("p");
          text.className = "text info center fundo cinza";
          text.textContent = "Nenhuma Opção Disponível";
          container.appendChild(text);
        }
      } else {
        create_popup(response.title, response.text, "Voltar");
      }
    });
}

function set_limitScroll(element_scroll, size_limit = 30) {
  const maxHeight = (size_limit * window.innerHeight) / 100;
  const size_element = element_scroll.scrollHeight;

  if (element_scroll.childElementCount) {
    if (size_element > maxHeight) {
      element_scroll.style.minHeight = `${parseInt(maxHeight)}px`;
    } else {
      element_scroll.style.minHeight = `${size_element}px`;
    }
  } else {
    element_scroll.style.minHeight = "0px";
  }
}

function setSortable(element) {
  element.sortable({
    handle: ".icon_move",
    tolerance: "pointer",
    forcePlaceholderSize: true,

    start: function (event, ui) {
      var icon = ui.item.find("i");
      var number = ui.item.find("h4");
      var text = ui.item.find("p");

      icon.addClass("shadow");
      icon.addClass("grabbing");
      number.addClass("shadow");
      text.addClass("shadow");
    },
    stop: function (event, ui) {
      var icon = ui.item.find("i");
      var number = ui.item.find("h4");
      var text = ui.item.find("p");

      set_sequence(ui.item[0]);
      icon.removeClass("grabbing");
      setTimeout(() => {
        icon.removeClass("shadow");
        number.removeClass("shadow");
        text.removeClass("shadow");
      }, 400);
    },
  });
}

function config_animate(index, item, name, duraction, value_initial, sum) {
  item.style.animation = `${name} ${duraction}s forwards ${
    value_initial + index * sum
  }s`;
}

function animate_itens(
  list_itens,
  animate = "fadeDown",
  duraction = 0.3,
  dalay_init = 0,
  interval_itens = 0.06,
  opacity = 0,
  exception = false
) {
  if (list_itens) {
    let list_execute = [];
    list_itens.forEach((item) => {
      if (exception) {
        if (
          !item.classList.contains("inactive") ||
          item.id.includes(exception)
        ) {
          list_execute.push(item);
        }
      } else {
        if (!item.classList.contains("inactive")) {
          list_execute.push(item);
        }
      }
    });

    list_execute.forEach((item, index) => {
      item.style.opacity = opacity;
      config_animate(
        index,
        item,
        animate,
        duraction,
        dalay_init,
        interval_itens
      );
    });
  }
}

function enterInterface(type, args = null, dalay = 0) {
  let elements = null;

  setTimeout(() => {
    switch (type) {
      case "login":
        elements = document.querySelectorAll('[class*="-enter-"]');
        animate_itens(elements, "fadeDown", 0.6, 0.55);

        const container = document.getElementById("container");
        container.style.transition =
          "border-radius 0.5s ease, height 0.85s ease 0.15s";
        container.classList.remove("container_complete");
        container.classList.add("enter--radius");

        break;

      case "register":
        elements = document.querySelectorAll('[class*="-enter-"]');
        animate_itens(elements, "fadeDown", 0.8, 0, 0.1);

        break;

      case "page_user":
        const header_enter = window.info_page.header;
        content.classList.remove("content_noBorder");

        setTimeout(() => {
          header_enter.classList.remove("header_hidden");
        }, 180);

        setTimeout(() => {
          header_enter.removeAttribute("style");
          nav.classList.remove("nav_hidden");
        }, 500);

        setTimeout(() => {
          replaceAba(null, args);
        }, 650);

        break;

      case "line":
        const name_line = document.getElementById("interface_nome").textContent;
        loadInterfaceLine(name_line);
        break;

      case "profile":
        loadProfile();
        elements = document.querySelectorAll('[class*="-enter-"]');
        animate_itens(elements, "fadeDown", 0.5, 0.2);

        break;
    }
  }, dalay);
}

function closeInterface(type, redirect = false, args = false, add_url = []) {
  let elements = null;

  function redirect_page(local, dalay = 0) {
    if (local) {
      setTimeout(() => {
        window.location.href = `/${local}`;
      }, dalay);
    }
  }

  if (add_url.length) {
    redirect = add_url.reduce((acc, value) => `${acc}/${encodeURIComponent(value)}`, redirect)
  }

  const popups = Array.from(document.getElementById("popup_local").children);
  if (popups.length) {
    popups.forEach((element) => {
      close_popup(element.id);
    });
  }

  switch (type) {
    case "login":
      const container = document.getElementById("container");
      container.style.transition =
        "border-radius 0.5s ease 0.4s, height 0.7s ease";

      setTimeout(() => {
        container.classList.remove("enter--radius");
        container.classList.add("container_complete");
      }, 300);
      elements = document.querySelectorAll(
        '[class*="-enter-"]:not(#container)'
      );
      animate_itens(elements, "outUp", 0.4, 0, 0.07, 1);
      setTimeout(() => {
        enterInterface("login", null, 50);
      }, 1000);
      redirect_page(redirect, 1010);

      break;

    case "register":
      const forms = document.querySelectorAll("form");
      forms.forEach((form) => {
        form.classList.add("-enter-");
      });
      elements = document.querySelectorAll(
        '[class*="-enter-"]:not(#container)'
      );
      animate_itens(elements, "outUp", 0.4, 0, 0.07, 1);
      setTimeout(() => {
        enterInterface("register", null, 50);
      }, 600);
      redirect_page(redirect, 610);

      break;

    case "page_user":
      header_close = window.info_page.header;
      let aba_atual = document.querySelector("i.page__icon--btn.selected").id;
      const aba = document.getElementById(`aba_${aba_atual}`);
      const itens = aba.querySelectorAll('[class*="-enter-"]');
      header_close.style.opacity = 0;

      if (redirect === "line") {
        const popup = document.getElementById('summary_line')
        let info = {
          principal: [extract_info(popup, "nome")],
          secondary: { local_page: aba_atual },
        };
        redirect += generate_url_dict(info);
      } else {
        redirect += `?local_page=${encodeURIComponent(aba_atual)}`;
      }

      setTimeout(() => {
        animate_itens(itens, "outUp", 0.5, 0, 0.03, 1);
      }, 100);

      setTimeout(() => {
        header_close.classList.add("header_hidden");
        nav.classList.add("nav_hidden");
      }, 150);

      setTimeout(() => {
        content.classList.add("content_noBorder");
      }, 400);

      setTimeout(() => {
        enterInterface("page_user", aba_atual, 50);
      }, 970);
      redirect_page(redirect, 1000);

      break;

    case "line":
      elements = document.querySelectorAll('[class*="-enter-"]');
      animate_itens(elements, "outUp", 0.5, 0, 0.03, 1);
      setTimeout(() => {
        enterInterface("line", null, 50);
      }, 640);
      redirect_page(`page_user?local=${encodeURIComponent(args)}`, 650);

      break;

    case "profile":
      elements = document.querySelectorAll('[class*="-enter-"]');
      animate_itens(elements, "outUp", 0.5, 0, 0.03, 1);

      if (args[1]) {
        close_popup("confirm_logout");
        fetch("/logout", { method: "GET" });
        redirect_page(redirect, 700);
      } else {
        setTimeout(() => {
          enterInterface("profile");
        }, 690);
        redirect_page(redirect + `?local=${encodeURIComponent(args[0])}`, 700);
      }

      break;
  }
}
