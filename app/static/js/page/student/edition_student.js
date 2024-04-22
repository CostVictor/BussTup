function edit_contraturno_fixo() {
  const container = document.getElementById("content_local_contraturno");
  const selected = container.querySelectorAll('[class*="selected"]');
  const data = [];
  selected.forEach((element) => {
    data.push(element.parentNode.querySelector("p").textContent);
  });

  popup_button_load("edit_contraturno");
  fetch("/edit_contraturno_fixo", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        close_popup("edit_contraturno");
        create_popup(response.title, response.text, "Ok", "success");
        loadWeek();
      } else {
        create_popup(response.title, response.text, "Voltar");
        popup_button_load("edit_contraturno", "Salvar");
      }
    });
}


function edit_dia() {
  const data = {
    'data': document.getElementById('data_dia').textContent,
    'faltara': return_bool_selected(document.getElementById('options_falta')),
    'contraturno': return_bool_selected(document.getElementById('options_contraturno'))
  }

  popup_button_load("edit_dia");
  fetch("/edit_day", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
  .then((response) => response.json())
  .then((response) => {
    if (!response.error) {
      close_popup("edit_dia");
      create_popup(response.title, response.text, "Ok", "success");
      loadWeek();
    } else {
      create_popup(response.title, response.text, "Voltar");
      popup_button_load("edit_dia", "Salvar");
    }
  });
}
