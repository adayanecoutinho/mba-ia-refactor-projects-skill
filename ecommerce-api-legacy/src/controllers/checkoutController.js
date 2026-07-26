// Controller de checkout: orquestra Models e Services e formata a
// resposta HTTP. A cadeia de callbacks aninhados do AppManager.js legado
// foi substituída por async/await (ver src/config/database.js).
const userModel = require('../models/userModel');
const courseModel = require('../models/courseModel');
const enrollmentModel = require('../models/enrollmentModel');
const paymentModel = require('../models/paymentModel');
const auditLogModel = require('../models/auditLogModel');
const passwordHasher = require('../utils/passwordHasher');
const { VALID_PAYMENT_STATUS, TEST_CARD_APPROVED_PREFIX } = require('../config');

async function checkout(req, res, { db, cache }) {
  const { usr: name, eml: email, pwd: password, c_id: courseId, card } = req.body;

  if (!name || !email || !courseId || !card) {
    return res.status(400).json({ error: 'Bad Request' });
  }

  const course = await courseModel.findActiveById(db, courseId);
  if (!course) {
    return res.status(404).json({ error: 'Curso não encontrado' });
  }

  let user = await userModel.findByEmail(db, email);
  if (!user) {
    const passwordHash = await passwordHasher.hash(password || '123456');
    const userId = await userModel.create(db, { name, email, passwordHash });
    user = { id: userId };
  }

  // Simulação de gateway de pagamento: nunca logar o número do cartão nem
  // a chave do gateway (o código legado fazia console.log dos dois juntos).
  const status = card.startsWith(TEST_CARD_APPROVED_PREFIX)
    ? VALID_PAYMENT_STATUS.PAID
    : VALID_PAYMENT_STATUS.DENIED;

  if (status === VALID_PAYMENT_STATUS.DENIED) {
    return res.status(400).json({ error: 'Pagamento recusado' });
  }

  const enrollmentId = await enrollmentModel.create(db, user.id, courseId);
  await paymentModel.create(db, enrollmentId, course.price, status);
  await auditLogModel.record(db, `Checkout curso ${courseId} por ${user.id}`);

  cache.set(`last_checkout_${user.id}`, course.title);

  return res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId });
}

module.exports = { checkout };
