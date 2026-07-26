// Tratamento de erro centralizado: substitui as respostas inconsistentes
// (`res.send(string)` vs `res.json(...)`) espalhadas pelo AppManager.js
// legado por um único formato de erro.
function errorHandler(err, req, res, _next) {
  // eslint-disable-next-line no-console
  console.error(err);
  res.status(500).json({ error: 'Erro interno do servidor' });
}

module.exports = errorHandler;
