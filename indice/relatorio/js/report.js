import { loadData } from '../../js/data.js';

loadData('../aggregates.json').then((N) => {
  console.info('[relatorio] dados carregados', N.hero);
}).catch((e) => {
  document.body.insertAdjacentHTML('afterbegin',
    `<p style="color:red;padding:1rem">Erro ao carregar dados: ${e.message}</p>`);
});
