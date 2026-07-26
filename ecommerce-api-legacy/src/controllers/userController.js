const userModel = require('../models/userModel');

async function deleteUser(req, res, { db }) {
  const { id } = req.params;
  await userModel.remove(db, id);
  // Nota: o código legado já deixava matrículas/pagamentos órfãos ao
  // deletar um usuário (achado MEDIUM do relatório de auditoria). O
  // contrato de resposta original foi preservado; a limpeza em cascata
  // fica documentada como próximo passo recomendado no README.
  return res.status(200).json({ message: 'Usuário deletado' });
}

module.exports = { deleteUser };
