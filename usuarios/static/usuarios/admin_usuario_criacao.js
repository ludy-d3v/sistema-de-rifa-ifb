(function () {
  function atualizarCamposVendedor() {
    var campoPapel = document.getElementById('id_papel');
    if (!campoPapel) {
      return;
    }

    var papel = campoPapel.value;
    var vendedorSelecionado = papel === 'vendedor';
    var camposVendedor = [
      '.form-row.field-organizador_vendedor',
      '.form-row.field-comissao_fixa'
    ];

    camposVendedor.forEach(function (seletor) {
      var linha = document.querySelector(seletor);
      if (!linha) {
        return;
      }

      linha.style.display = vendedorSelecionado ? '' : 'none';
      linha.querySelectorAll('select, input').forEach(function (campo) {
        campo.disabled = !vendedorSelecionado;
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var campoPapel = document.getElementById('id_papel');
    atualizarCamposVendedor();
    if (campoPapel) {
      campoPapel.addEventListener('change', atualizarCamposVendedor);
    }
  });
})();
